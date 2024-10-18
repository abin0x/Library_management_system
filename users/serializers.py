from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from django.db.models import Max
import re

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    profile_image = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password',
            'confirm_password', 'phone_number', 'address', 'date_of_birth',
            'employee_id', 'profile_image'
        ]
        read_only_fields = ['employee_id']

    def validate(self, data):
        # Validate if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'error': "Passwords don't match"})
        
        # Check if email already exists
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'error': "This email is already registered"})

        return data

    def create(self, validated_data):
        # Get the validated data excluding confirm_password
        validated_data.pop('confirm_password')
        
        # Create the new user
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password

        # Set user type to 'librarian'
        user.user_type = 'librarian'  # Set to 'librarian' regardless of input

        # Additional behavior for librarian user_type
        user.employee_id = ''  # Will be auto-generated in model save method

        user.is_active = False  # Set user as inactive initially (for email verification, etc.)
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Account is not active. Please confirm your email.")
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'profile_image', 'phone_number', 'address']


class LibrarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'profile_image', 'phone_number', 'address', 'employee_id']
        read_only_fields = ['employee_id']  # Employee ID should not be editable




from rest_framework import serializers
from .models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from random import randint

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'user_id': {'read_only': True}  # Make user_id read-only as it's auto-generated
        }

    def create(self, validated_data):
        # Create a user instance without saving it to the database yet
        user = User(**validated_data)
        user.save()  # This will automatically set user_id using the overridden save method
        return user


class UserLoginSerializer(serializers.Serializer):
    userId = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['userId'], password=data['password'])
        if user is None:
            print(f"Failed login for userId: {data['userId']}")  # Log the failing userId
            raise serializers.ValidationError("Invalid login credentials")
        return user

