from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    CategoryListCreateAPIView, CategoryDetailAPIView,
    AuthorListCreateAPIView, AuthorDetailAPIView,
    BookListCreateAPIView, BookDetailAPIView,
    IssueBookView, UserBorrowHistoryView,
    ReturnBookAPIView,DueBooksView,DueBooksReportView,OverdueBooksView,AdminDashboardAPIView,BorrowHistoryView,IndividualBorrowDetailView,AvailableBooksListView,NewUserBorrowHistoryView
)

urlpatterns = [
    # Category URLs
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    
    # Author URLs
    path('authors/', AuthorListCreateAPIView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', AuthorDetailAPIView.as_view(), name='author-detail'),
    
    # Book URLs
    path('books/', BookListCreateAPIView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),

    # Issue and Return URLs
    path('issue-book/', IssueBookView.as_view(), name='issue-book'),
    path('return-book/<int:pk>/', ReturnBookAPIView.as_view(), name='return-book'),

    # User Borrow History
    path('user-borrow-history/<int:user_id>/', NewUserBorrowHistoryView.as_view(), name='user-borrow-history'),
    # path('user-borrow-history/<int:user_id>/', UserBorrowHistoryView.as_view(), name='user-borrow-history'),
    path('due-books/', DueBooksView.as_view(), name='due-books'),
    path('due-books-report/', DueBooksReportView.as_view(), name='due-books-report'),
    path('overdue-books/', OverdueBooksView.as_view(), name='overdue-books'),
    path('dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),

    path('borrow/', BorrowHistoryView.as_view(), name='borrow-history'),
    path('borrow/<int:pk>/', IndividualBorrowDetailView.as_view(), name='individual-borrow-detail'),
    path('available-books-report/', AvailableBooksListView.as_view(), name='available-books-report'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)