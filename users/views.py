from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer
from .models import CustomUser,User
from django.contrib.auth import authenticate

class UserRegistrationAPIView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Generate email confirmation token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"http://127.0.0.1:8000/api/users/activate/{uid}/{token}/"
            email_subject = "Confirm Your Email"

            # Select email template based on user type
            if user.user_type == 'librarian':
                email_template = 'librarian_verification_email.html'
            else:
                email_template = 'user_verification_email.html'

            # Render email body
            email_body = render_to_string(email_template, {'confirm_link': confirm_link})

            # Send the email
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()

            return Response({"detail": "Check your email for confirmation"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('http://127.0.0.1:5500/login_register.html')  # Redirect to your login page
    else:
        return redirect('register')  # Redirect to your registration page on failure


class UserLoginApiView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "user_type": user.user_type,
                "profile_image": user.profile_image.url if user.profile_image else None,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)





    
class UserLogoutAPIView(APIView):
    def get(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response({"detail": "Logged out successfully."})



class UserListAPIView(APIView):
    def get(self, request):
        users = CustomUser.objects.all()  # You can filter based on user type if needed
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.pagination import PageNumberPagination

class MemberPagination(PageNumberPagination):
    page_size = 10  # Number of members per page
    page_size_query_param = '1'
    max_page_size = 100


# class MemberListAPIView(APIView):
#     def get(self, request):
#         # Filter users by user type 'member'
#         members = CustomUser.objects.filter(user_type='member')
#         # paginator = MemberPagination()
#         # paginated_members = paginator.paginate_queryset(members, request)
#         member_count = members.count()  # Count the number of members

#         # Serialize the member data
#         serializer = UserSerializer(members, many=True)
#         # serializer = UserSerializer(paginated_members, many=True)
        
#         # Prepare the response data
#         # return paginator.get_paginated_response(serializer.data)
#         response_data = {
#             'member_count': member_count,
#             'members': serializer.data
#         }
        
#         return Response(response_data, status=status.HTTP_200_OK)
from django.db.models import Q
class MemberListAPIView(APIView):
    def get(self, request):
        # Get the search query
        search_query = request.GET.get('search', '')

        # Filter users by user type 'member' and the search query
        members = CustomUser.objects.filter(user_type='member')

        if search_query:
            members = members.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )

        member_count = members.count()  # Count the number of members

        # Pagination logic
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)
        start = (int(page) - 1) * int(limit)
        end = start + int(limit)
        members = members[start:end]

        # Serialize the member data
        serializer = UserSerializer(members, many=True)
        
        # Prepare the response data
        response_data = {
            'member_count': member_count,
            'members': serializer.data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



class MemberDetailAPIView(APIView):
    def get(self, request, member_id):
        try:
            member = CustomUser.objects.get(id=member_id, user_type='member')
            serializer = UserSerializer(member)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, member_id):
        try:
            member = CustomUser.objects.get(id=member_id, user_type='member')
            serializer = UserSerializer(member, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, member_id):
        try:
            member = CustomUser.objects.get(id=member_id, user_type='member')
            member.delete()
            return Response({'message': 'Member deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the logged-in user
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Allow partial updates to the user profile
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)



class TeacherDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    # permission_classes = [CanViewTeacherDetail]
    
    def get_queryset(self):
        # Filter only teachers
        return CustomUser.objects.filter(user_type='librarian')

class StudentDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    # permission_classes = [CanViewStudentDetail]
    
    def get_queryset(self):
        # Filter only students
        return CustomUser.objects.filter(user_type='member')
    

from .serializers import UserRegistrationSerializer

class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class LoginView(APIView):
    def post(self, request):
        userId = request.data.get("userId")  # Update to get userId
        password = request.data.get("password")

        # Use username instead of studentid in the authenticate function
        user = authenticate(username=userId, password=password)  

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "user_type": user.user_type,
                "profile_image": user.profile_image.url if user.profile_image else None,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



