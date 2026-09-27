"""
Hiring views for Skill Swap.

Handles hire request lifecycle: create, accept, reject, start, complete, cancel.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.permissions import IsVerifiedAndActive
from apps.notifications.models import Notification
from .models import HireRequest
from .serializers import (
    HireRequestSerializer,
    HireRequestCreateSerializer,
    HireRequestStatusSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Hiring']),
    retrieve=extend_schema(tags=['Hiring']),
    create=extend_schema(tags=['Hiring']),
    update=extend_schema(tags=['Hiring']),
    partial_update=extend_schema(tags=['Hiring']),
    destroy=extend_schema(tags=['Hiring']),
)
class HireRequestViewSet(viewsets.ModelViewSet):
    """
    CRUD for hire requests.

    - Clients create hire requests targeting a provider.
    - Providers accept/reject incoming requests.
    - Both parties can view their hire requests.
    - Status transitions are handled via the /status/ action.
    """

    permission_classes = [IsAuthenticated, IsVerifiedAndActive]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'budget', 'deadline']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Users see hire requests where they are the client or provider."""
        user = self.request.user
        return HireRequest.objects.filter(
            Q(client=user) | Q(provider=user)
        ).select_related('client', 'provider')

    def get_serializer_class(self):
        if self.action == 'create':
            return HireRequestCreateSerializer
        if self.action == 'update_status':
            return HireRequestStatusSerializer
        return HireRequestSerializer

    def perform_create(self, serializer):
        hire_request = serializer.save()
        
        Notification.objects.create(
            user=hire_request.provider,
            title='New Hire Request',
            message=f'{hire_request.client.get_full_name()} has sent you a hire request for "{hire_request.title}".',
            type=Notification.Type.HIRE_REQUEST,
            data={'hire_request_id': hire_request.id}
        )

    def perform_destroy(self, instance):
        """Only pending requests can be deleted, and only by the client."""
        if instance.client != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the client can delete a hire request.')
        if instance.status != HireRequest.Status.PENDING:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Only pending requests can be deleted.')
        instance.delete()

    @extend_schema(
        request=HireRequestStatusSerializer,
        responses={200: HireRequestSerializer},
        tags=['Hiring'],
    )
    @action(detail=True, methods=['post'], url_path='status')
    def update_status(self, request, pk=None):
        """
        POST /api/hiring/{id}/status/

        Transition the hire request to a new status.
        Actions: accept, reject, start, complete, cancel.
        """
        hire_request = self.get_object()
        serializer = HireRequestStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_name = serializer.validated_data['action']
        user = request.user

        # Define valid transitions
        transitions = {
            'accept': {
                'allowed_by': 'provider',
                'from': [HireRequest.Status.PENDING],
                'to': HireRequest.Status.ACCEPTED,
            },
            'reject': {
                'allowed_by': 'provider',
                'from': [HireRequest.Status.PENDING],
                'to': HireRequest.Status.REJECTED,
            },
            'start': {
                'allowed_by': 'provider',
                'from': [HireRequest.Status.ACCEPTED],
                'to': HireRequest.Status.IN_PROGRESS,
            },
            'complete': {
                'allowed_by': 'client',
                'from': [HireRequest.Status.IN_PROGRESS],
                'to': HireRequest.Status.COMPLETED,
            },
            'cancel': {
                'allowed_by': 'both',
                'from': [
                    HireRequest.Status.PENDING,
                    HireRequest.Status.ACCEPTED,
                    HireRequest.Status.IN_PROGRESS,
                ],
                'to': HireRequest.Status.CANCELLED,
            },
        }

        transition = transitions.get(action_name)
        if not transition:
            return Response(
                {'success': False, 'message': f'Unknown action: {action_name}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check permissions
        allowed_by = transition['allowed_by']
        if allowed_by == 'provider' and user != hire_request.provider:
            return Response(
                {'success': False, 'message': 'Only the provider can perform this action.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if allowed_by == 'client' and user != hire_request.client:
            return Response(
                {'success': False, 'message': 'Only the client can perform this action.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if allowed_by == 'both' and user not in (hire_request.client, hire_request.provider):
            return Response(
                {'success': False, 'message': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check valid transition
        if hire_request.status not in transition['from']:
            return Response(
                {
                    'success': False,
                    'message': f'Cannot {action_name} a request with status "{hire_request.status}".',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Apply transition
        hire_request.status = transition['to']
        if action_name == 'reject':
            hire_request.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        if action_name == 'complete':
            hire_request.completed_at = timezone.now()
        hire_request.save()

        # Generate notifications and automated messages
        if action_name == 'accept':
            Notification.objects.create(
                user=hire_request.client,
                title='Hire Request Accepted',
                message=f'{hire_request.provider.get_full_name()} has accepted your hire request for "{hire_request.title}".',
                type=Notification.Type.HIRE_ACCEPTED,
                data={'hire_request_id': hire_request.id}
            )
        elif action_name == 'reject':
            Notification.objects.create(
                user=hire_request.client,
                title='Hire Request Rejected',
                message=f'{hire_request.provider.get_full_name()} has declined your hire request for "{hire_request.title}".',
                type=Notification.Type.HIRE_REJECTED,
                data={'hire_request_id': hire_request.id}
            )
        elif action_name == 'start':
            # Check if a conversation already exists
            from apps.messaging.models import Message
            has_messaged = Message.objects.filter(
                (Q(sender=hire_request.client, receiver=hire_request.provider) |
                 Q(sender=hire_request.provider, receiver=hire_request.client))
            ).exists()
            
            if not has_messaged:
                # Create an automated first message from provider to client
                Message.objects.create(
                    sender=hire_request.provider,
                    receiver=hire_request.client,
                    hire_request=hire_request,
                    content=f"Hi, I have started the job for '{hire_request.title}'. Let's discuss the details here.",
                    is_read=False
                )
        elif action_name == 'complete':
            # Notify the other party that the job was marked complete
            other_user = hire_request.provider if user == hire_request.client else hire_request.client
            Notification.objects.create(
                user=other_user,
                title='Job Completed',
                message=f'{user.get_full_name()} marked the job "{hire_request.title}" as completed.',
                type=Notification.Type.HIRE_COMPLETED,
                data={'hire_request_id': hire_request.id}
            )

        return Response({
            'success': True,
            'message': f'Hire request {action_name}ed successfully.',
            'data': HireRequestSerializer(hire_request).data,
        })

    @extend_schema(
        responses={200: dict},
        tags=['Hiring'],
    )
    @action(detail=False, methods=['post'], url_path='mark-seen')
    def mark_seen(self, request):
        """
        POST /api/hiring/mark-seen/

        Mark all incoming hire requests for the current user as seen.
        """
        user = request.user
        updated_count = HireRequest.objects.filter(
            provider=user,
            is_seen=False,
            status=HireRequest.Status.PENDING
        ).update(is_seen=True)

        return Response({
            'success': True,
            'message': f'Marked {updated_count} incoming requests as seen.',
        })
