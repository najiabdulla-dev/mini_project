"""
Review model for Skill Swap.

Users can review each other after completing a hire request.
Reviews include a 1-5 star rating, written comment, and optional screenshot.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.models import SoftDeleteModel


class Review(SoftDeleteModel):
    """
    A review from one user to another, tied to a completed hire request.

    Only one review per hire request per direction is allowed
    (reviewer → reviewee for a specific hire request).
    """

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
    )
    hire_request = models.ForeignKey(
        'hiring.HireRequest',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True, default='')
    screenshot = models.ImageField(
        upload_to='review_screenshots/', blank=True, null=True,
    )
    is_reported = models.BooleanField(
        default=False, db_index=True,
        help_text='Flagged as potentially fake or abusive',
    )

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['reviewer', 'reviewee', 'hire_request']
        indexes = [
            models.Index(fields=['reviewee', 'rating'], name='idx_review_reviewee'),
            models.Index(fields=['hire_request'], name='idx_review_hire'),
        ]

    def __str__(self):
        return f'{self.reviewer.email} → {self.reviewee.email}: {self.rating}★'
