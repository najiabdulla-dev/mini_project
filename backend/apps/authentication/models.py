"""
User and OTP models for Skill Swap.

The User model supports a single account acting as both skill provider and client.
Only Admin status is tracked via `is_admin`. All other users can both offer and hire.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from utils.validators import validate_phone_number, validate_github_url, validate_linkedin_url


class UserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for Skill Swap.

    Design decision: A single account can act as both a skill provider (offering services)
    and a client (hiring others). There is no separate "User" vs "Client" role — all
    registered users have both capabilities. Only Admin is a distinct role.

    Profile fields are stored directly on the User model for simplicity in Phase 1.
    This avoids an extra join for every profile fetch.
    """

    class Availability(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        BUSY = 'busy', 'Busy'
        OFFLINE = 'offline', 'Offline'

    # -------------------------------------------------------------------------
    # Auth fields — email replaces username
    # -------------------------------------------------------------------------
    username = None
    email = models.EmailField('email address', unique=True, db_index=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # -------------------------------------------------------------------------
    # Profile fields
    # -------------------------------------------------------------------------
    phone = models.CharField(
        max_length=20, blank=True, default='',
        validators=[validate_phone_number],
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/', blank=True, null=True,
    )
    bio = models.TextField(blank=True, default='', max_length=1000)
    location = models.CharField(max_length=200, blank=True, default='')
    github_url = models.URLField(
        blank=True, default='',
        validators=[validate_github_url],
    )
    linkedin_url = models.URLField(
        blank=True, default='',
        validators=[validate_linkedin_url],
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Default hourly rate in USD',
    )
    languages = models.JSONField(
        default=list, blank=True,
        help_text='List of languages spoken, e.g. ["English", "Hindi"]',
    )
    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
        db_index=True,
    )

    # -------------------------------------------------------------------------
    # Status fields
    # -------------------------------------------------------------------------
    is_admin = models.BooleanField(
        default=False, db_index=True,
        help_text='Designates whether this user has admin/moderator privileges.',
    )
    is_verified = models.BooleanField(
        default=True, db_index=True,
        help_text='Designates whether this user has verified their email.',
    )
    is_active = models.BooleanField(default=True)

    # -------------------------------------------------------------------------
    # Soft delete
    # -------------------------------------------------------------------------
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['is_verified', 'is_active'], name='idx_user_status'),
            models.Index(fields=['availability'], name='idx_user_availability'),
            models.Index(fields=['location'], name='idx_user_location'),
        ]

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    def soft_delete(self):
        """Mark user as deleted without removing from database."""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted user."""
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'is_active', 'deleted_at', 'updated_at'])



