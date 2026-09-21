"""
Authentication serializers for Skill Swap.

Handles: registration, login (JWT), OTP verification,
forgot/reset password, profile retrieval, password change.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

from .models import User
from utils.validators import validate_password_strength





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that adds user info to the response.
    Returns access + refresh tokens along with user profile data.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        # Check if user is verified
        if not user.is_verified:
            from utils.exceptions import AccountNotVerifiedError
            raise AccountNotVerifiedError()

        # Check if user is deleted
        if user.is_deleted:
            from utils.exceptions import AccountDeactivatedError
            raise AccountDeactivatedError()

        # Add user data to response
        data['user'] = UserSerializer(user).data

        return data

    @classmethod
    def get_token(cls, user):
        """Add custom claims to the JWT token."""
        token = super().get_token(user)
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        token['full_name'] = user.get_full_name()
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only user profile serializer.
    Used in login responses and profile endpoints.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'profile_photo', 'bio', 'location',
            'github_url', 'linkedin_url', 'hourly_rate',
            'languages', 'availability',
            'is_admin', 'is_verified',
            'created_at', 'updated_at', 'last_login',
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile fields.
    Email and password are updated via separate endpoints.
    """

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'profile_photo',
            'bio', 'location', 'github_url', 'linkedin_url',
            'hourly_rate', 'languages', 'availability',
        ]

    def validate_phone(self, value):
        if value:
            from utils.validators import validate_phone_number
            validate_phone_number(value)
        return value
