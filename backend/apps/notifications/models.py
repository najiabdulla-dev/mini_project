"""
Notification model for Skill Swap.

In-app notifications for hire requests, messages, reviews, system alerts, etc.
FCM push delivery will be wired in Phase 2.
"""

from django.db import models
from django.conf import settings
from utils.models import TimestampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Notification(TimestampedModel):
    """
    In-app notification for a user.

    Notifications are created by the system when events happen
    (new hire request, message, review, etc.) and are displayed
    in the user's notification feed.
    """

    class Type(models.TextChoices):
        HIRE_REQUEST = 'hire_request', 'Hire Request'
        HIRE_ACCEPTED = 'hire_accepted', 'Hire Accepted'
        HIRE_REJECTED = 'hire_rejected', 'Hire Rejected'
        HIRE_COMPLETED = 'hire_completed', 'Hire Completed'
        MESSAGE = 'message', 'New Message'
        REVIEW = 'review', 'New Review'
        PROFILE_VIEW = 'profile_view', 'Profile View'
        SYSTEM = 'system', 'System Announcement'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        db_index=True,
    )
    data = models.JSONField(
        default=dict, blank=True,
        help_text='Additional context data (e.g., hire_request_id, sender_id)',
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at'], name='idx_notif_user'),
            models.Index(fields=['type', '-created_at'], name='idx_notif_type'),
        ]

    def __str__(self):
        return f'{self.title} → {self.user.email}'

@receiver(post_save, sender=Notification)
def broadcast_notification(sender, instance, created, **kwargs):
    if created:
        from apps.notifications.serializers import NotificationSerializer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.user.id}',
            {
                'type': 'new_notification',
                'notification': NotificationSerializer(instance).data
            }
        )
