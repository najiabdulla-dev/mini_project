"""
Message model for Skill Swap.

Supports 1:1 messaging between users, optionally linked to a hire request.
Real-time delivery via Django Channels will be added in Phase 2.
"""

from django.db import models
from django.conf import settings
from utils.models import TimestampedModel


class Message(TimestampedModel):
    """
    A single message between two users.

    Messages can be linked to a HireRequest for context,
    or be standalone direct messages.
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
    )
    hire_request = models.ForeignKey(
        'hiring.HireRequest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messages',
        help_text='Optional: link message to a hire request conversation',
    )
    content = models.TextField()
    attachment = models.FileField(
        upload_to='message_attachments/', blank=True, null=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(
                fields=['sender', 'receiver', '-created_at'],
                name='idx_message_conversation',
            ),
            models.Index(
                fields=['receiver', 'is_read'],
                name='idx_message_unread',
            ),
            models.Index(
                fields=['hire_request', 'created_at'],
                name='idx_message_hire',
            ),
        ]

    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f'{self.sender.email} → {self.receiver.email}: {preview}'
