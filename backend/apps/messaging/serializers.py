"""
Messaging serializers for Skill Swap.
"""

from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Read serializer for messages."""

    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name',
            'receiver', 'receiver_name',
            'hire_request', 'content', 'attachment',
            'is_read', 'read_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'sender', 'sender_name', 'receiver_name',
            'is_read', 'read_at', 'created_at', 'updated_at',
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    """Write serializer for sending messages."""

    class Meta:
        model = Message
        fields = ['id', 'receiver', 'hire_request', 'content', 'attachment']
        read_only_fields = ['id']

    def validate_receiver(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError('You cannot message yourself.')
        if not value.is_active or value.is_deleted:
            raise serializers.ValidationError('This user is no longer available.')
        return value

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationSerializer(serializers.Serializer):
    """Serializer for conversation list (latest message per partner)."""

    partner_id = serializers.IntegerField()
    partner_name = serializers.CharField()
    partner_email = serializers.EmailField()
    partner_photo = serializers.ImageField(allow_null=True)
    last_message = serializers.CharField()
    last_message_at = serializers.DateTimeField()
    unread_count = serializers.IntegerField()
