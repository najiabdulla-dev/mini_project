"""
Hiring request model for Skill Swap.

Represents a client hiring a skill provider. Tracks the full lifecycle:
Pending → Accepted → In Progress → Completed (or Rejected/Cancelled at any stage).
"""

from django.db import models
from django.conf import settings
from utils.models import TimestampedModel


class HireRequest(TimestampedModel):
    """
    A hire request from a client to a skill provider.

    The client creates the request; the provider accepts/rejects.
    Both parties can negotiate or cancel.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_hire_requests',
        help_text='The user who is hiring',
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_hire_requests',
        help_text='The user being hired',
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    deadline = models.DateField(null=True, blank=True)
    attachments = models.JSONField(
        default=list, blank=True,
        help_text='List of attachment URLs',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    rejection_reason = models.TextField(blank=True, default='')
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'hire_requests'
        verbose_name = 'Hire Request'
        verbose_name_plural = 'Hire Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'status'], name='idx_hire_client'),
            models.Index(fields=['provider', 'status'], name='idx_hire_provider'),
            models.Index(fields=['status', '-created_at'], name='idx_hire_status'),
        ]

    def __str__(self):
        return f'{self.title} ({self.client.email} → {self.provider.email})'
