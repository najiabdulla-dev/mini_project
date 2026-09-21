"""
Admin panel models for Skill Swap.

Key-value settings store for platform-wide configuration.
"""

from django.db import models


class AdminSettings(models.Model):
    """
    Key-value store for platform-wide admin settings.

    Examples:
        - platform_name: "Skill Swap"
        - maintenance_mode: "false"
        - max_upload_size_mb: "10"
        - featured_categories: "[1, 3, 5]"
    """

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True, default='')
    description = models.CharField(
        max_length=300, blank=True, default='',
        help_text='Human-readable description of this setting',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_settings'
        verbose_name = 'Admin Setting'
        verbose_name_plural = 'Admin Settings'
        ordering = ['key']

    def __str__(self):
        return f'{self.key} = {self.value[:50]}'

    @classmethod
    def get_setting(cls, key, default=''):
        """Get a setting value by key, returning default if not found."""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, key, value, description=''):
        """Set a setting value by key, creating it if it doesn't exist."""
        obj, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description},
        )
        return obj
