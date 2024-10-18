from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Field to track active/inactive status

    def __str__(self):
        return self.name


from django.db import models

class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Book(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn_number = models.CharField(max_length=13, unique=True)  # ISBN-13
    publisher = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField(default=0)  
    available = models.BooleanField(default=True)
    cover_image = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)   # Add this line
    updated_at = models.DateTimeField(auto_now=True)  

    def save(self, *args, **kwargs):
        # Ensure total_quantity is updated whenever a book is saved
        if self.pk is not None:  # If the book already exists
            orig = Book.objects.get(pk=self.pk)
            self.total_quantity = orig.total_quantity
        else:
            self.total_quantity = self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class IssuedBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Update this line
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Track fine amount
    is_fine_paid = models.BooleanField(default=False)  # Track if fine is paid

    def is_late(self):
        return timezone.now() > self.due_date
    
    # def calculate_fine(self):
    #     if self.is_late() and not self.is_fine_paid:
    #         days_late = (self.return_date - self.due_date).days
    #         fine_rate_per_day = 1.00  # Set your fine rate per day here
    #         self.fine_amount = days_late * fine_rate_per_day
    #     else:
    #         self.fine_amount = 0.00