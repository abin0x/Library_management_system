from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    )

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    # profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='librarian')

    def save(self, *args, **kwargs):
        # Only generate employee ID if the user is a librarian and the employee ID is not already set
        if self.user_type == 'librarian' and not self.employee_id:
            last_employee = CustomUser.objects.filter(user_type='librarian').order_by('id').last()
            if last_employee and last_employee.employee_id:
                try:
                    last_id = int(last_employee.employee_id[3:])  # Extract the numeric part of the employee ID
                    self.employee_id = f'EMP{last_id + 1:03}'  # Increment and format as EMP###
                except ValueError:
                    # Handle cases where employee_id does not have a valid numeric part
                    self.employee_id = 'EMP001'
            else:
                self.employee_id = 'EMP001'  # Start with EMP001 for the first librarian

        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return self.username

    



from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, userId, password=None, **extra_fields):
        if not userId:
            raise ValueError('The User must have a userId')
        
        user = self.model(userId=userId, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userId, password=None, **extra_fields):
        user = self.create_user(userId, password, **extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    user_id = models.CharField(max_length=10, unique=True, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = User.objects.order_by('id').last()  # Get the last user by ID
            if last_user:
                last_user_number = int(last_user.user_id.replace('USER', ''))
                self.user_id = f'USER{last_user_number + 1:03}'  # Increment the number and format
            else:
                self.user_id = 'USER001'  # Start from USER001
        super().save(*args, **kwargs)

