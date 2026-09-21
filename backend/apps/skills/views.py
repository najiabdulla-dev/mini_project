"""
Skill and Category views for Skill Swap.

Categories and skills are read-only for regular users.
Only admins can create, update, or delete.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.permissions import IsAdmin, IsVerifiedAndActive
from .models import Category, Skill
from .serializers import CategorySerializer, SkillSerializer, SkillCreateSerializer


@extend_schema_view(
    list=extend_schema(tags=['Skills']),
    retrieve=extend_schema(tags=['Skills']),
    create=extend_schema(tags=['Skills']),
    update=extend_schema(tags=['Skills']),
    partial_update=extend_schema(tags=['Skills']),
    destroy=extend_schema(tags=['Skills']),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for skill categories.

    - GET (list/retrieve): Any authenticated user
    - POST/PUT/PATCH/DELETE: Admin only
    """

    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']

    def get_queryset(self):
        qs = Category.objects.all()
        if not self.request.user.is_admin:
            qs = qs.filter(is_active=True)
        return qs

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.soft_delete()


@extend_schema_view(
    list=extend_schema(tags=['Skills']),
    retrieve=extend_schema(tags=['Skills']),
    create=extend_schema(tags=['Skills']),
    update=extend_schema(tags=['Skills']),
    partial_update=extend_schema(tags=['Skills']),
    destroy=extend_schema(tags=['Skills']),
)
class SkillViewSet(viewsets.ModelViewSet):
    """
    CRUD for skills.

    - GET (list/retrieve): Any authenticated user
    - POST/PUT/PATCH/DELETE: Admin only
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        qs = Skill.objects.select_related('category').all()
        if not self.request.user.is_admin:
            qs = qs.filter(is_active=True, category__is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SkillCreateSerializer
        return SkillSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.soft_delete()
