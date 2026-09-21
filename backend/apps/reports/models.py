"""
Report model for Skill Swap.

Users can report other users, reviews, or content for admin moderation.
"""

from django.db import models
from django.conf import settings
from utils.models import TimestampedModel


class Report(TimestampedModel):
    """
    A user-submitted report for moderation.

    Reports can target a user profile or a specific review.
    Admins review reports and resolve them.
    """

    class Type(models.TextChoices):
        USER = 'user', 'User Report'
        REVIEW = 'review', 'Review Report'
        SPAM = 'spam', 'Spam'
        FAKE_PROFILE = 'fake_profile', 'Fake Profile'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        REVIEWED = 'reviewed', 'Under Review'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_filed',
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='reports_against',
    )
    reported_review = models.ForeignKey(
        'reviews.Review',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='reports',
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        db_index=True,
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    admin_notes = models.TextField(
        blank=True, default='',
        help_text='Internal notes by admin handling the report',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at'], name='idx_report_status'),
            models.Index(fields=['type', 'status'], name='idx_report_type'),
        ]

    def __str__(self):
        target = self.reported_user.email if self.reported_user else f'Review #{self.reported_review_id}'
        return f'Report by {self.reporter.email} against {target} ({self.status})'
