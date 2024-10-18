from django.urls import path
from .views import (
    
    activate,UserRegistrationAPIView,UserLoginApiView,UserLogoutAPIView,UserListAPIView,UserProfileAPIView,TeacherDetailAPIView,StudentDetailAPIView,AdminCreateUserView,LoginView,MemberListAPIView,MemberDetailAPIView
)

urlpatterns = [
    # User management URLs
    path('register/', UserRegistrationAPIView.as_view(), name='register'),  # User registration
    path('login/', UserLoginApiView.as_view(), name='login'),  # User login
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),  # User logout
    # path('activate/<uid64>/<token>/', activate, name='activate'), 
    path('users/activate/<uid64>/<token>/', activate, name='activate'),
    path('list/', UserListAPIView.as_view(), name='user-list'),  # List all users
    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),  # User profile management
    path('librarian/<int:pk>/', TeacherDetailAPIView.as_view(), name='teacher-detail'),  # Teacher detail endpoint
    path('just/member/<int:pk>/', StudentDetailAPIView.as_view(), name='student-detail'),  # Student detail endpoint
    path('admin/create-user/', AdminCreateUserView.as_view(), name='admin-create-user'),
    path('member/login/', LoginView.as_view(), name='user-login'),
    # path('dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('userslist/', MemberListAPIView.as_view(), name='user-list'),
    path('members/<int:member_id>/', MemberDetailAPIView.as_view(), name='member-detail'),
  
]
