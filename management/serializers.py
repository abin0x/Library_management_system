from rest_framework import serializers
from .models import Category,Book,Author,IssuedBook,User
from users.models import User

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'created_at', 'updated_at', 'is_active']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

from rest_framework import serializers
from .models import Author

# class AuthorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Author
#         fields = ['id', 'first_name', 'last_name', 'created_at', 'updated_at']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name']

# class BookSerializer(serializers.ModelSerializer):
#     # category = CategorySerializer() 
#     # author = AuthorSerializer(read_only=True)
    
#     class Meta:
#         model = Book
#         fields = ['id', 'name', 'category', 'author', 'isbn_number', 'publisher', 'price', 'quantity', 'available', 'cover_image']

class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())  # Use ID for input, but will display details
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Use ID for input, but will display details

    # These fields will be displayed with nested details in the response
    author_details = AuthorSerializer(source='author', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'name', 'category', 'category_details', 'author', 'author_details', 'isbn_number', 'publisher', 'price', 'quantity', 'available', 'cover_image']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# class IssuedBookSerializer(serializers.ModelSerializer):
#     book = BookSerializer(allow_null=True)  # Allowing null
#     user = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = IssuedBook
#         fields = ['id', 'user', 'book', 'issue_date', 'due_date']

from rest_framework import serializers
from .models import IssuedBook

# class IssuedBookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IssuedBook
#         fields = ['id', 'user', 'book', 'issue_date','due_date', 'return_date', 'fine_amount', 'is_fine_paid']


class IssuedBookSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)  # Add user name
    book_title = serializers.CharField(source='book.name', read_only=True)  # Add book title

    class Meta:
        model = IssuedBook
        fields = ['id', 'user', 'user_name', 'book', 'book_title', 'issue_date', 'due_date', ]
        # fields = ['id', 'user', 'book', 'issue_date', 'due_date', ]
        read_only_fields = ['issue_date']  # Make issue_date read-only to set automatically on creation
        

    def validate(self, attrs):
        user = attrs.get('user')
        book = attrs.get('book')

        # Check if the user has already borrowed this book and not returned it
        if IssuedBook.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("You cannot borrow this book until you return the current copy.")
        
        # Check if the book has available quantity
        if book.quantity <= 0:  # Assuming the 'quantity' field exists on the Book model
            raise serializers.ValidationError("No available quantity of this book.")

        return attrs



# class ReturnBookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IssuedBook
#         fields = '__all__'  # or explicitly list the fields you want to serialize


# from rest_framework import serializers

# class ReturnBookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IssuedBook
#         fields = [ 'user', 'book','return_date', 'fine_amount', 'is_fine_paid']  # Include user and book fields

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation['user'] = instance.user.username  # Change to a desired field like username
#         representation['book'] = instance.book.title  # Change to a desired field like title
#         return representation


class ReturnBookSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Use nested serializer for user
    book = BookSerializer(read_only=True)  # Use nested serializer for book

    class Meta:
        model = IssuedBook
        fields = [ 'user', 'book','return_date', 'fine_amount', 'is_fine_paid']



from rest_framework import serializers
from .models import IssuedBook
from django.utils import timezone
class DueBookReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)  # Add user name
    book_title = serializers.CharField(source='book.name', read_only=True)  # Add book title
    overdue_days = serializers.SerializerMethodField()  # Field to calculate overdue days

    class Meta:
        model = IssuedBook
        fields = ['id', 'user_name', 'book_title', 'issue_date', 'due_date', 'overdue_days']

    def get_overdue_days(self, obj):
        # Calculate overdue days only if the book is overdue
        if obj.return_date is None and obj.due_date < timezone.now():
            overdue_days = (timezone.now().date() - obj.due_date.date()).days
            return overdue_days
        return 0  # Return 0 if the book is not overdue



class NewIssuedBookSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.name', read_only=True)
    return_status = serializers.SerializerMethodField()  # Add return status field

    class Meta:
        model = IssuedBook
        fields = ['id', 'user', 'user_name', 'book', 'book_title', 'issue_date', 'due_date', 'return_date', 'return_status']
        read_only_fields = ['issue_date']

    def get_return_status(self, obj):
        return 'Returned' if obj.return_date else 'Not Returned'  # Determine the return status
