"""
Bookmark views for Skill Swap.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.permissions import IsVerifiedAndActive
from .models import Bookmark
from .serializers import BookmarkSerializer, BookmarkCreateSerializer


@extend_schema_view(
    list=extend_schema(tags=['Bookmarks']),
    retrieve=extend_schema(tags=['Bookmarks']),
    create=extend_schema(tags=['Bookmarks']),
    destroy=extend_schema(tags=['Bookmarks']),
)
class BookmarkViewSet(viewsets.ModelViewSet):
    """
    Bookmarks API.

    - GET /api/bookmarks/ — list saved profiles
    - POST /api/bookmarks/ — bookmark a user
    - DELETE /api/bookmarks/{id}/ — remove bookmark
    - POST /api/bookmarks/toggle/ — toggle bookmark for a user
    """

    permission_classes = [IsAuthenticated, IsVerifiedAndActive]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user,
        ).select_related('bookmarked_user')

    def get_serializer_class(self):
        if self.action == 'create':
            return BookmarkCreateSerializer
        return BookmarkSerializer

    @extend_schema(
        request=BookmarkCreateSerializer,
        tags=['Bookmarks'],
    )
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        POST /api/bookmarks/toggle/

        Toggle bookmark for a user. If already bookmarked, removes it.
        If not bookmarked, creates one.
        """
        from apps.authentication.models import User

        bookmarked_user_id = request.data.get('bookmarked_user')
        if not bookmarked_user_id:
            return Response(
                {'success': False, 'message': 'bookmarked_user is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            bookmarked_user = User.objects.get(pk=bookmarked_user_id)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'message': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if bookmarked_user == request.user:
            return Response(
                {'success': False, 'message': 'You cannot bookmark yourself.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user, bookmarked_user=bookmarked_user,
        )

        if not created:
            bookmark.delete()
            return Response({
                'success': True,
                'message': 'Bookmark removed.',
                'is_bookmarked': False,
            })

        return Response({
            'success': True,
            'message': 'User bookmarked.',
            'is_bookmarked': True,
            'data': BookmarkSerializer(bookmark).data,
        }, status=status.HTTP_201_CREATED)
