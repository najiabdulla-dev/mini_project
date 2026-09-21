"""
Notification serializers for Skill Swap.
"""

from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Read serializer for notifications."""

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'type',
            'data', 'is_read', 'read_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields
