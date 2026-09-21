"""
Notification views for Skill Swap.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.permissions import IsVerifiedAndActive
from .models import Notification
from .serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(tags=['Notifications']),
    retrieve=extend_schema(tags=['Notifications']),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Notifications API (read-only — notifications are system-generated).

    - GET /api/notifications/ — list notifications
    - GET /api/notifications/{id}/ — retrieve a notification
    - POST /api/notifications/{id}/read/ — mark as read
    - POST /api/notifications/read-all/ — mark all as read
    - GET /api/notifications/unread-count/ — get unread count
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsVerifiedAndActive]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(tags=['Notifications'])
    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        """POST /api/notifications/{id}/read/ — Mark a notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        return Response({
            'success': True,
            'message': 'Notification marked as read.',
            'data': NotificationSerializer(notification).data,
        })

    @extend_schema(tags=['Notifications'])
    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        """POST /api/notifications/read-all/ — Mark all notifications as read."""
        count = Notification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        return Response({
            'success': True,
            'message': f'{count} notifications marked as read.',
        })

    @extend_schema(tags=['Notifications'])
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """GET /api/notifications/unread-count/ — Get unread notification count."""
        count = Notification.objects.filter(
            user=request.user, is_read=False,
        ).count()
        return Response({
            'unread_count': count,
        })
