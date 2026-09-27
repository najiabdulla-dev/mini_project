"""
Custom permission classes for Skill Swap.

Role-based and ownership-based permission checks used across all apps.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to admin users."""

    message = 'Admin access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsVerified(BasePermission):
    """Allow access only to email-verified users."""

    message = 'Please verify your email to access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_email_verified
        )


class IsActiveUser(BasePermission):
    """Allow access only to active (non-deleted) users."""

    message = 'Your account has been deactivated.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and not request.user.is_deleted
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Allow access to the owner of the object or admin users.
    The object must have a `user` or `user_id` attribute.
    """

    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True

        # Check various ownership patterns
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
        if hasattr(obj, 'client'):
            return obj.client == request.user
        if hasattr(obj, 'provider'):
            return obj.provider == request.user

        return False


class IsOwner(BasePermission):
    """
    Allow access only to the owner of the object.
    Does NOT allow admin override (use IsOwnerOrAdmin for that).
    """

    message = 'You can only access your own resources.'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id
        return False


class IsVerifiedAndActive(BasePermission):
    """Combined check: user must be both verified and active."""

    message = 'Your account must be verified and active.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_email_verified
            and request.user.is_active
            and not request.user.is_deleted
        )
