"""
Messaging views for Skill Swap.

REST-based 1:1 messaging. Real-time via WebSockets will be added later.
"""

from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Max, Count, Subquery, OuterRef
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.models import User
from apps.authentication.permissions import IsVerifiedAndActive
from .models import Message
from .serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    ConversationSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Messaging']),
    retrieve=extend_schema(tags=['Messaging']),
    create=extend_schema(tags=['Messaging']),
)
class MessageViewSet(viewsets.ModelViewSet):
    """
    Messages API.

    - GET /api/messages/ — list messages (filter by partner or hire_request)
    - POST /api/messages/ — send a message
    - GET /api/messages/{id}/ — retrieve a message
    - POST /api/messages/{id}/read/ — mark as read
    """

    permission_classes = [IsAuthenticated, IsVerifiedAndActive]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver')

        # Filter by conversation partner
        partner_id = self.request.query_params.get('partner')
        if partner_id:
            qs = qs.filter(
                Q(sender_id=partner_id) | Q(receiver_id=partner_id)
            )

        # Filter by hire request
        hire_id = self.request.query_params.get('hire_request')
        if hire_id:
            qs = qs.filter(hire_request_id=hire_id)

        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def retrieve(self, request, *args, **kwargs):
        """Mark message as read when the receiver retrieves it."""
        instance = self.get_object()
        if instance.receiver == request.user and not instance.is_read:
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save(update_fields=['is_read', 'read_at'])
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        responses={200: MessageSerializer},
        tags=['Messaging'],
    )
    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        """POST /api/messages/{id}/read/ — Mark a message as read."""
        message = self.get_object()
        if message.receiver != request.user:
            return Response(
                {'success': False, 'message': 'You can only mark your own messages as read.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        message.is_read = True
        message.read_at = timezone.now()
        message.save(update_fields=['is_read', 'read_at'])
        return Response({
            'success': True,
            'message': 'Message marked as read.',
            'data': MessageSerializer(message).data,
        })

    @extend_schema(tags=['Messaging'])
    @action(detail=False, methods=['get'], url_path='conversations')
    def conversations(self, request):
        """
        GET /api/messages/conversations/

        List all conversations (unique chat partners) with the latest message
        and unread count for each.
        """
        user = request.user

        # Get all unique conversation partners
        sent_to = Message.objects.filter(sender=user).values_list('receiver_id', flat=True)
        received_from = Message.objects.filter(receiver=user).values_list('sender_id', flat=True)
        partner_ids = set(sent_to) | set(received_from)

        conversations = []
        for partner_id in partner_ids:
            try:
                partner = User.objects.get(pk=partner_id)
            except User.DoesNotExist:
                continue

            last_msg = Message.objects.filter(
                (Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user))
            ).order_by('-created_at').first()

            unread = Message.objects.filter(
                sender=partner, receiver=user, is_read=False,
            ).count()

            if last_msg:
                conversations.append({
                    'partner_id': partner.id,
                    'partner_name': partner.get_full_name(),
                    'partner_email': partner.email,
                    'partner_photo': partner.profile_photo if partner.profile_photo else None,
                    'last_message': last_msg.content[:100],
                    'last_message_at': last_msg.created_at,
                    'unread_count': unread,
                })

        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message_at'], reverse=True)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Messaging'])
    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        """POST /api/messages/read-all/ — Mark all unread messages as read."""
        partner_id = request.data.get('partner')
        qs = Message.objects.filter(receiver=request.user, is_read=False)
        if partner_id:
            qs = qs.filter(sender_id=partner_id)
        count = qs.update(is_read=True, read_at=timezone.now())
        return Response({
            'success': True,
            'message': f'{count} messages marked as read.',
        })
