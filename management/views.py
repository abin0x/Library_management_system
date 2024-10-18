from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Category,Author,Book,IssuedBook,User
from .serializers import CategorySerializer,AuthorSerializer,BookSerializer,IssuedBookSerializer
from users .serializers import UserSerializer
from django.conf import settings
from rest_framework.views import APIView
from django.db.models import Sum
from .serializers import ReturnBookSerializer,NewIssuedBookSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model 
from rest_framework.exceptions import NotFound
User = get_user_model()
# List and Create Categories
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        total_categories = Category.objects.count()
        response.data = {
            'categories': response.data,
            'total_categories': total_categories
        }
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        total_categories = Category.objects.count()
        response.data['total_categories'] = total_categories
        return response


# Toggle Category active/inactive status
class CategoryToggleActiveView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        category = self.get_object()
        category.is_active = not category.is_active  # Toggle the active status
        category.save()
        return Response({'status': 'success', 'message': 'Category status updated', 'is_active': category.is_active})


# Retrieve, Update, and Delete Category
class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAdminUser]


# List and Create Authors
class AuthorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Get the list of all authors
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Get the total count of authors
        total_authors = queryset.count()

        # Return the list of authors and the total count in a single response
        return Response({
            "authors": serializer.data,
            "total_authors": total_authors
        })

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        total_authors = Author.objects.count()  # Get the total number of authors after creation
        response.data['total_authors'] = total_authors
        return response
    
# Retrieve, Update, and Delete Author
class AuthorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # permission_classes = [IsAdminUser]

class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # permission_classes = [IsAdminUser]



# class BookListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

#     def get_queryset(self):
#         # Only return books that are marked as available
#         return Book.objects.filter(available=True)


#     def list(self, request, *args, **kwargs):
#         response = super().list(request, *args, **kwargs)

        
#         total_borrowed_books = IssuedBook.objects.filter(return_date__isnull=True).count()
        
#         # Correctly access the quantity from the serialized data
#         total_available_books = sum(book['quantity'] for book in response.data if book['quantity'] > 0)
#         total_books = total_available_books + total_borrowed_books
#         # Calculate total fines for all users
#         total_fines = IssuedBook.objects.filter(return_date__isnull=True).aggregate(
#         total_fine=Sum('fine_amount')
#         )['total_fine'] or 0.00  # Default to 0 if None

#         response.data = {
#             'total_books': total_books,
#             'total_available_books': total_available_books,
#             'total_borrowed_books': total_borrowed_books,
#             'books': response.data,
#             'total_fines': total_fines  # Include total fines in the response
#         }

#         return Response(response.data)



from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Sum

class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()  # Fetch all books
    serializer_class = BookSerializer

    def get_queryset(self):
        # Return all books regardless of availability
        return Book.objects.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        total_borrowed_books = IssuedBook.objects.filter(return_date__isnull=True).count()
        
        # Calculate total available books
        total_available_books = sum(book['quantity'] for book in response.data if book['available'] and book['quantity'] > 0)
        total_books = len(response.data)  # Total books shown (including unavailable ones)
        
        # Calculate total fines for all users
        total_fines = IssuedBook.objects.filter(return_date__isnull=True).aggregate(
            total_fine=Sum('fine_amount')
        )['total_fine'] or 0.00  # Default to 0 if None

        response.data = {
            'total_books': total_books,
            'total_available_books': total_available_books,
            'total_borrowed_books': total_borrowed_books,
            'books': response.data,
            'total_fines': total_fines  # Include total fines in the response
        }

        return Response(response.data)




class IssueBookView(APIView):
    serializer_class = IssuedBookSerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the incoming data

        user_id = request.data.get('user')  # Fetch user ID from validated data
        book_id = request.data.get('book')  # Fetch book ID from validated data
        due_days = request.data.get('due_days', 0)  # Default due_days to 14 if not provided

        try:
            user = User.objects.get(id=user_id)  # Fetch user by ID
            book = Book.objects.get(id=book_id)  # Fetch book by ID


            # Check if the user has already borrowed this book and not returned it
            if IssuedBook.objects.filter(user=user, book=book, return_date__isnull=True).exists():
                return Response({'error': 'You cannot borrow this book until you return the current copy.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check available copies before issuing
            available_copies = book.quantity - IssuedBook.objects.filter(book=book, return_date=None).count()
            if available_copies <= 0:
                return Response({'error': 'No copies available to issue.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create an IssuedBook record
            due_date = timezone.now() + timedelta(days=due_days)
            issued_book = IssuedBook.objects.create(
                user=user,
                book=book,
                due_date=due_date,
                # fine_amount=request.data.get('fine_amount', 0.00),  
                # is_fine_paid=request.data.get('is_fine_paid', False)  
            )

            # Reduce the quantity of the book by 1
            book.quantity -= 1
            book.save()  # Save the updated quantity

            return Response({
                'message': 'Book issued successfully',
                'due_date': issued_book.due_date,
                'total_books': Book.objects.count(),
                'total_available_books': book.quantity,
                'total_borrowed_books': IssuedBook.objects.filter(return_date=None).count()
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



# Return Book
# class ReturnBookAPIView(generics.UpdateAPIView):
#     serializer_class = ReturnBookSerializer
#     queryset = IssuedBook.objects.all()
#     permission_classes = [IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         issued_book = self.get_object()

#         if issued_book.return_date is not None:
#             return Response({'error': 'Book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

#         issued_book.return_date = timezone.now()
#         issued_book.save()
#         # Calculate fine if the book is returned late
#         if issued_book.is_late():
#             late_days = (issued_book.return_date - issued_book.due_date).days
#             fine_per_day = 1.00  # Set your fine per day
#             issued_book.fine = late_days * fine_per_day
#         else:
#             issued_book.fine_amount = 0  # No fine if returned on time
        
#         issued_book.is_fine_paid = False  # Mark as unpaid initially
#         issued_book.save()
#         # Increase available books count
#         book = issued_book.book
#         book.quantity += 1
#         book.save()

#         return Response({
#             'message': 'Book returned successfully.',
#             'fine': issued_book.fine_amount,
#             'is_fine_paid': issued_book.is_fine_paid,
#         }, status=status.HTTP_200_OK)


# Return Book
# class ReturnBookAPIView(generics.UpdateAPIView):
#     serializer_class = ReturnBookSerializer
#     queryset = IssuedBook.objects.all()
#     permission_classes = [IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         issued_book = self.get_object()
#         # Check if the book is already returned
#         if issued_book.return_date is not None:
#             return Response({'error': 'This book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Update the return date
#         issued_book.return_date = timezone.now()
#         issued_book.calculate_fine()  # Calculate the fine if any
#         issued_book.is_fine_paid = False  # Set fine payment status to unpaid (if applicable)
#         issued_book.save()

#         # Update the book's quantity
#         book = issued_book.book
#         book.quantity += 1  # Increase the available quantity
#         book.save()  # Save the updated quantity

#         return Response({
#             'message': 'Book returned successfully.',
#             'fine_amount': issued_book.fine_amount,
#             'updated_quantity': book.quantity,
#         }, status=status.HTTP_200_OK)


# class ReturnBookAPIView(generics.UpdateAPIView):
#     serializer_class = ReturnBookSerializer
#     queryset = IssuedBook.objects.all()
#     permission_classes = [IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         issued_book = self.get_object()
        
#         # Check if the book is already returned
#         if issued_book.return_date is not None:
#             return Response({'error': 'This book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Update the return date
#         issued_book.return_date = timezone.now()

#         # If the return date is past the due date, allow admin to set fine
#         if issued_book.is_late():
#             fine_amount = request.data.get('fine_amount', 0.00)  # Admin can set this in the request
#             issued_book.fine_amount = fine_amount
#             issued_book.is_fine_paid = request.data.get('is_fine_paid', False)  # Admin can indicate if fine is paid
#         else:
#             issued_book.fine_amount = 0.00
#             issued_book.is_fine_paid = True  # Fine is considered paid if it's returned on time

#         issued_book.save()

#         # Update the book's quantity
#         book = issued_book.book
#         book.quantity += 1  # Increase the available quantity
#         book.save()  # Save the updated quantity

#         return Response({
#             'message': 'Book returned successfully.',
#             'fine_amount': issued_book.fine_amount,
#             'is_fine_paid': issued_book.is_fine_paid,
#             'updated_quantity': book.quantity,
#         }, status=status.HTTP_200_OK)

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import IssuedBook
from .serializers import ReturnBookSerializer

class ReturnBookAPIView(generics.UpdateAPIView):
    serializer_class = ReturnBookSerializer
    queryset = IssuedBook.objects.all()
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        issued_book = self.get_object()

        # Check if the book is already returned
        if issued_book.return_date is not None:
            return Response({'error': 'This book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the return date
        issued_book.return_date = timezone.now()

        # Handle fine charging if the book is returned late
        if issued_book.is_late():
            # Check if the user making the request is an admin (staff)
            if request.user.is_staff:
                fine_amount = request.data.get('fine_amount', issued_book.fine_amount)
                issued_book.fine_amount = fine_amount
                issued_book.is_fine_paid = True  # Automatically set as True since admin charged the fine
            else:
                return Response({'error': 'Only admin can set fine charges for late returns.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            issued_book.fine_amount = 0.00
            issued_book.is_fine_paid = True  # No fine if returned on time

        issued_book.save()

        # Update the book's quantity
        book = issued_book.book
        book.quantity += 1  # Increase the available quantity
        book.save()  # Save the updated quantity

        # Use the updated ReturnBookSerializer to return the response
        serializer = self.get_serializer(issued_book)

        return Response({
            'message': 'Book returned successfully.',
            'fine_amount': issued_book.fine_amount,
            'is_fine_paid': issued_book.is_fine_paid,
            'updated_quantity': book.quantity,
            'return_data': serializer.data,
        }, status=status.HTTP_200_OK)






class UserBorrowHistoryView(generics.ListAPIView):
    serializer_class = IssuedBookSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = IssuedBook.objects.filter(user_id=user_id)

        if not queryset.exists():
            raise NotFound("No borrow history found for this user.")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_borrowed_books = queryset.count()

        # Calculate total fines for this user
        # total_fines = sum(book.fine_amount for book in queryset if not book.is_fine_paid)
        total_fines = sum(book.fine_amount for book in queryset if not book.is_fine_paid)
        # Calculate total books and available books
        total_books = Book.objects.count()
        total_available_books = Book.objects.filter(quantity__gt=0).count()
        returned_books_count = queryset.filter(return_date__isnull=False).count()
        # Include individual fines in the borrow history response
        borrow_history_with_fines = [
            {
                'book_id': book.book.id,
                'book_title': book.book.name,
                'issue_date': book.issue_date,
                'due_date': book.due_date,
                'return_date': book.return_date,
                'fine_amount': book.fine_amount,
                'is_fine_paid': book.is_fine_paid
            } for book in queryset
        ]

        return Response({
            'not_returned_books': total_borrowed_books - returned_books_count,
            'total_borrowed_books': total_borrowed_books,
            'total_fines': total_fines,
            'returned_books_count': returned_books_count,
            'borrow_history': serializer.data
        })



from .serializers import DueBookReportSerializer
class DueBooksReportView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the total count of due books
        total_due_books = IssuedBook.objects.filter(return_date__isnull=True, due_date__lt=timezone.now()).count()
        
        # Get the list of due books
        due_books = IssuedBook.objects.filter(return_date__isnull=True, due_date__lt=timezone.now())
        due_books_serializer = DueBookReportSerializer(due_books, many=True)

        # Get the usernames of members who have due books
        members_with_due_books = User.objects.filter(
            id__in=due_books.values_list('user', flat=True)
        ).values_list('username', flat=True)

        return Response({
            'total_due_books': total_due_books,
            'due_books': due_books_serializer.data,
            'members_with_due_books': list(members_with_due_books),
        }, status=200)



class DueBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all due books
        total_due_books = IssuedBook.objects.filter(return_date__isnull=True, due_date__lt=timezone.now()).count()
        
        # Get due books for the specific user
        user_due_books = IssuedBook.objects.filter(user=user, return_date__isnull=True, due_date__lt=timezone.now())
        user_due_books_count = user_due_books.count()

        # Serialize the user's due books
        serializer = IssuedBookSerializer(user_due_books, many=True)

        return Response({
            'total_due_books': total_due_books,
            'user_due_books_count': user_due_books_count,
            'user_due_books': serializer.data  # This will include details of due books for the user
        }, status=200)
    


class OverdueBooksView(APIView):
    def get(self, request):
        # Get the current date and time
        now = timezone.now()
        
        # Fetch overdue issued books
        overdue_books = IssuedBook.objects.filter(due_date__lt=now, return_date__isnull=True)

        # Prepare the response data
        result = {}
        for issued_book in overdue_books:
            user = issued_book.user.username  # Get the username of the user
            book_title = issued_book.book.name  # Get the title of the book

            if user not in result:
                result[user] = []  # Initialize a list for this user if not already present
            
            # Append the book title and due date to the user's list
            result[user].append({
                'book_title': book_title,
                'due_date': issued_book.due_date
            })

        return Response(result, status=status.HTTP_200_OK)
    



    # ------------------admin------------- 

from django.db import models 
class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Calculate the total available books based on the quantity
        # total_available_books = Book.objects.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        total_available_books = Book.objects.filter(available=True).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0

        # Borrowed books (books that have not been returned yet)
        total_borrowed_books = IssuedBook.objects.filter(return_date__isnull=True).count()

        # Calculate the total books as the sum of available and borrowed books
        total_books = total_available_books + total_borrowed_books

        # Total members (users with user_type = 'member')
        total_members = User.objects.filter(user_type='member').count()

        # Overdue books (books that are past the due date and have not been returned)
        total_overdue_books = IssuedBook.objects.filter(due_date__lt=timezone.now(), return_date__isnull=True).count()

        # Total categories
        total_categories = Category.objects.count()

        # Total authors
        total_authors = Author.objects.count()
        # Calculate the total fines collected from all users
        total_fines_collected = IssuedBook.objects.filter(is_fine_paid=True).aggregate(total_fines=models.Sum('fine_amount'))['total_fines'] or 0.00

        data = {
            'total_books': total_books,
            'total_available_books': total_available_books,
            'total_borrowed_books': total_borrowed_books,
            'total_members': total_members,
            'total_overdue_books': total_overdue_books,
            'total_categories': total_categories,
            'total_authors': total_authors,
            'total_fines_collected': total_fines_collected,  # Total fines collected from users
        }

        return Response(data, status=status.HTTP_200_OK)
    




class BorrowHistoryView(generics.ListAPIView):
    serializer_class = IssuedBookSerializer

    def get_queryset(self):
        # Filter queryset for currently borrowed books (not returned)
        queryset = IssuedBook.objects.filter(return_date__isnull=True)

        if not queryset.exists():
            raise NotFound("No current borrow history found.")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Calculate total fines across all records
        total_fines = sum(book.fine_amount for book in queryset if not book.is_fine_paid)
        
        # Count total currently borrowed books
        total_borrowed_books = queryset.count()
        # Get the current time for calculating duration
        current_time = timezone.now()  # Get the current time

        # Build the response structure with individual records
        borrow_history = []
        for issued_book in queryset:
            # Calculate duration in days since the issue date
            duration_days = (current_time.date() - issued_book.issue_date.date()).days
            
            # Ensure duration is not negative
            duration = max(0, duration_days)  # Set to 0 if negative
            
            # Calculate remaining time until due date in days
            remaining_time = (issued_book.due_date.date() - current_time.date()).days
            
            # Ensure remaining time is not negative
            remaining_days = max(0, remaining_time)  # Set to 0 if negative

            borrow_history.append({
                "id": issued_book.id,
                "user": issued_book.user.id,  # Keep the user ID
                "user_name": issued_book.user.username,  # Add user name
                "book": issued_book.book.id,  # Keep the book ID
                "book_title": issued_book.book.name,  # Add book title
                "issue_date": issued_book.issue_date,
                "due_date": issued_book.due_date,
                "fine_amount": issued_book.fine_amount,
                "is_fine_paid": issued_book.is_fine_paid,
                
                "remaining_time": remaining_days  # Remaining days until due date
            })

        return Response({
            'total_borrowed_books': total_borrowed_books,
            'total_fines': total_fines,
            'borrow_history': borrow_history  # Use the custom borrow history list
        })



class IndividualBorrowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = IssuedBook.objects.all()
    serializer_class = IssuedBookSerializer

    def get_object(self):
        """Retrieve an IssuedBook instance by its ID."""
        try:
            return super().get_object()
        except IssuedBook.DoesNotExist:
            raise NotFound("The specified borrowed book record does not exist.")

    def get(self, request, *args, **kwargs):
        """Retrieve a specific borrowed book record."""
        issued_book = self.get_object()
        serializer = self.get_serializer(issued_book)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """Update a specific borrowed book record."""
        issued_book = self.get_object()
        serializer = self.get_serializer(issued_book, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """Delete a specific borrowed book record without affecting the book itself."""
        issued_book = self.get_object()
        
        # Update book's available count
        book = issued_book.book  # Get the associated book
        book.quantity += 1  # Increase available books by 1
        
        # Optionally, if you have a field for the specific book quantity, you can also increase it
        # Assuming there's a field like `quantity` in your Book model
        # book.quantity += 1  # This could be another way to track if you are managing book quantities
        
        book.save()  # Save the book instance to update available books

        issued_book.delete()  # Now delete the issued book record
        return Response(status=204)
    

class AvailableBooksListView(generics.ListAPIView):
    # Queryset to fetch books that are available and have a quantity greater than 0
    queryset = Book.objects.filter(available=True, quantity__gt=0)
    serializer_class = BookSerializer

    def get_queryset(self):
        # Override the get_queryset method to return books that are available and have quantity > 0
        return Book.objects.filter(available=True, quantity__gt=0)
    

# -------------------------- User Borrow history new-------------------------

class NewUserBorrowHistoryView(generics.ListAPIView):
    serializer_class = NewIssuedBookSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = IssuedBook.objects.filter(user_id=user_id)

        if not queryset.exists():
            raise NotFound("No borrow history found for this user.")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_borrowed_books = queryset.count()

        total_fines = sum(book.fine_amount for book in queryset if book.is_fine_paid)
        total_books = Book.objects.count()
        total_available_books = Book.objects.filter(quantity__gt=0).count()
        returned_books_count = queryset.filter(return_date__isnull=False).count()

        return Response({
            'not_returned_books': total_borrowed_books - returned_books_count,
            'total_borrowed_books': total_borrowed_books,
            'total_fines': total_fines,
            'returned_books_count': returned_books_count,
            'borrow_history': serializer.data
        })
