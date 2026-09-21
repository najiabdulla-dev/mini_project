"""
Abstract base models for Skill Swap.

Provides TimestampedModel and SoftDeleteModel mixins that all app models
should inherit from for consistent timestamps and soft-delete behavior.
"""

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """
    Default manager that filters out soft-deleted records.
    Use `all_with_deleted()` to include deleted records.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """Return all records including soft-deleted ones."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(is_deleted=True)


class TimestampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at timestamps.
    All app models should inherit from this.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(TimestampedModel):
    """
    Abstract base model with soft-delete support.
    Records are never physically deleted — they are marked as deleted
    and filtered out of default querysets.

    Usage:
        instance.soft_delete()   — mark as deleted
        instance.restore()       — restore a deleted record
        Model.objects.all()      — excludes deleted records (default)
        Model.objects.all_with_deleted() — includes deleted records
        Model.objects.deleted_only()     — only deleted records
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Fallback manager — no filtering

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Mark this record as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def delete(self, using=None, keep_parents=False):
        """Override delete to perform soft delete by default."""
        self.soft_delete()

    def hard_delete(self, using=None, keep_parents=False):
        """Actually delete the record from the database."""
        super().delete(using=using, keep_parents=keep_parents)
