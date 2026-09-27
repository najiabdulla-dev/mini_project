"""
Django admin configuration for User and OTP models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model."""

    model = User
    list_display = [
        'email', 'first_name', 'last_name', 'is_email_verified',
        'is_admin', 'is_active', 'availability', 'created_at',
    ]
    list_filter = [
        'is_email_verified', 'is_admin', 'is_active', 'is_deleted',
        'availability', 'created_at',
    ]
    search_fields = ['email', 'first_name', 'last_name', 'location']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone', 'profile_photo',
                'bio', 'location', 'github_url', 'linkedin_url',
                'hourly_rate', 'languages', 'availability',
            ),
        }),
        ('Status', {
            'fields': (
                'is_email_verified', 'is_admin', 'is_active',
                'is_staff', 'is_superuser', 'is_deleted', 'deleted_at',
            ),
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name',
                'password1', 'password2',
                'is_admin', 'is_email_verified',
            ),
        }),
    )
