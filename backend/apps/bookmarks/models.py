"""
Bookmark model for Skill Swap.

Users can bookmark/save other users' profiles for easy access later.
"""

from django.db import models
from django.conf import settings
from utils.models import TimestampedModel


class Bookmark(TimestampedModel):
    """
    A bookmark/save of another user's profile.
    A user cannot bookmark themselves.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text='The user who created the bookmark',
    )
    bookmarked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_by',
        help_text='The user whose profile was bookmarked',
    )

    class Meta:
        db_table = 'bookmarks'
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        unique_together = ['user', 'bookmarked_user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_bookmark_user'),
        ]

    def __str__(self):
        return f'{self.user.email} bookmarked {self.bookmarked_user.email}'

    def clean(self):
        """Prevent users from bookmarking themselves."""
        from django.core.exceptions import ValidationError
        if self.user == self.bookmarked_user:
            raise ValidationError('You cannot bookmark your own profile.')
