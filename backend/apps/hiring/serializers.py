"""
Hiring serializers for Skill Swap.
"""

from rest_framework import serializers
from .models import HireRequest


class HireRequestSerializer(serializers.ModelSerializer):
    """Read serializer for hire requests with user info."""

    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client_email = serializers.EmailField(source='client.email', read_only=True)
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    provider_email = serializers.EmailField(source='provider.email', read_only=True)

    class Meta:
        model = HireRequest
        fields = [
            'id', 'client', 'client_name', 'client_email',
            'provider', 'provider_name', 'provider_email',
            'title', 'description', 'budget', 'deadline',
            'attachments', 'status', 'rejection_reason',
            'completed_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'client', 'client_name', 'client_email',
            'provider_name', 'provider_email',
            'status', 'rejection_reason', 'completed_at',
            'created_at', 'updated_at',
        ]


class HireRequestCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating hire requests."""

    class Meta:
        model = HireRequest
        fields = [
            'id', 'provider', 'title', 'description',
            'budget', 'deadline', 'attachments',
        ]
        read_only_fields = ['id']

    def validate_provider(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError('You cannot hire yourself.')
        if not value.is_active or value.is_deleted:
            raise serializers.ValidationError('This user is no longer available.')
        return value

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        validated_data['status'] = HireRequest.Status.PENDING
        return super().create(validated_data)

    def to_representation(self, instance):
        # Return the full representation including client details
        return HireRequestSerializer(instance, context=self.context).data


class HireRequestStatusSerializer(serializers.Serializer):
    """Serializer for status transition actions."""

    action = serializers.ChoiceField(
        choices=['accept', 'reject', 'start', 'complete', 'cancel'],
    )
    rejection_reason = serializers.CharField(required=False, allow_blank=True, default='')
