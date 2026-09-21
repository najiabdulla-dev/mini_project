"""
Review views for Skill Swap.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.permissions import IsVerifiedAndActive, IsOwnerOrAdmin
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


@extend_schema_view(
    list=extend_schema(tags=['Reviews']),
    retrieve=extend_schema(tags=['Reviews']),
    create=extend_schema(tags=['Reviews']),
    update=extend_schema(tags=['Reviews']),
    partial_update=extend_schema(tags=['Reviews']),
    destroy=extend_schema(tags=['Reviews']),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD for reviews.

    - GET /api/reviews/ — list reviews (filter by reviewee for a user's profile)
    - POST /api/reviews/ — create a review (only for completed hire requests)
    - PUT/PATCH /api/reviews/{id}/ — update own review
    - DELETE /api/reviews/{id}/ — soft-delete own review
    """

    permission_classes = [IsAuthenticated, IsVerifiedAndActive]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reviewee', 'reviewer', 'hire_request', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.select_related(
            'reviewer', 'reviewee', 'hire_request',
        ).all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsVerifiedAndActive(), IsOwnerOrAdmin()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        """Only the reviewer can delete their own review."""
        if instance.reviewer != self.request.user and not self.request.user.is_admin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only delete your own reviews.')
        instance.soft_delete()
