"""
Profile views for Skill Swap.

Handles CRUD for: UserSkill, Experience, Education, Certificate, Portfolio.
Also provides a public user profile endpoint.
"""

from rest_framework import viewsets, generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.authentication.models import User
from apps.authentication.permissions import IsOwnerOrAdmin, IsVerifiedAndActive
from .models import UserSkill, Experience, Education, Certificate, Portfolio
from .serializers import (
    UserSkillSerializer,
    UserSkillCreateSerializer,
    ExperienceSerializer,
    EducationSerializer,
    CertificateSerializer,
    PortfolioSerializer,
    UserProfileSerializer,
)


class BaseProfileViewSet(viewsets.ModelViewSet):
    """
    Base viewset for profile sub-resources.
    Automatically scopes queryset to the current user and sets user on create.
    """

    permission_classes = [IsAuthenticated, IsVerifiedAndActive]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if obj.user != request.user and not request.user.is_admin:
            self.permission_denied(request, message='You can only manage your own profile.')


@extend_schema_view(
    list=extend_schema(tags=['Profile — Skills']),
    retrieve=extend_schema(tags=['Profile — Skills']),
    create=extend_schema(tags=['Profile — Skills']),
    update=extend_schema(tags=['Profile — Skills']),
    partial_update=extend_schema(tags=['Profile — Skills']),
    destroy=extend_schema(tags=['Profile — Skills']),
)
class UserSkillViewSet(BaseProfileViewSet):
    """CRUD for the current user's skills."""

    queryset = UserSkill.objects.select_related('skill', 'skill__category').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['proficiency', 'is_active', 'skill__category']
    ordering_fields = ['created_at', 'years_experience', 'price']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UserSkillCreateSerializer
        return UserSkillSerializer


@extend_schema_view(
    list=extend_schema(tags=['Profile — Experience']),
    retrieve=extend_schema(tags=['Profile — Experience']),
    create=extend_schema(tags=['Profile — Experience']),
    update=extend_schema(tags=['Profile — Experience']),
    partial_update=extend_schema(tags=['Profile — Experience']),
    destroy=extend_schema(tags=['Profile — Experience']),
)
class ExperienceViewSet(BaseProfileViewSet):
    """CRUD for the current user's work experiences."""

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    ordering = ['-start_date']


@extend_schema_view(
    list=extend_schema(tags=['Profile — Education']),
    retrieve=extend_schema(tags=['Profile — Education']),
    create=extend_schema(tags=['Profile — Education']),
    update=extend_schema(tags=['Profile — Education']),
    partial_update=extend_schema(tags=['Profile — Education']),
    destroy=extend_schema(tags=['Profile — Education']),
)
class EducationViewSet(BaseProfileViewSet):
    """CRUD for the current user's education entries."""

    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    ordering = ['-start_date']


@extend_schema_view(
    list=extend_schema(tags=['Profile — Certificates']),
    retrieve=extend_schema(tags=['Profile — Certificates']),
    create=extend_schema(tags=['Profile — Certificates']),
    update=extend_schema(tags=['Profile — Certificates']),
    partial_update=extend_schema(tags=['Profile — Certificates']),
    destroy=extend_schema(tags=['Profile — Certificates']),
)
class CertificateViewSet(BaseProfileViewSet):
    """CRUD for the current user's certificates."""

    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    ordering = ['-issue_date']


@extend_schema_view(
    list=extend_schema(tags=['Profile — Portfolio']),
    retrieve=extend_schema(tags=['Profile — Portfolio']),
    create=extend_schema(tags=['Profile — Portfolio']),
    update=extend_schema(tags=['Profile — Portfolio']),
    partial_update=extend_schema(tags=['Profile — Portfolio']),
    destroy=extend_schema(tags=['Profile — Portfolio']),
)
class PortfolioViewSet(BaseProfileViewSet):
    """CRUD for the current user's portfolio items."""

    queryset = Portfolio.objects.select_related('skill').all()
    serializer_class = PortfolioSerializer
    ordering = ['-created_at']


@extend_schema(tags=['Profiles'])
class UserProfileView(generics.RetrieveAPIView):
    """
    GET /api/profiles/<id>/

    View any user's public profile with all their skills, experience,
    education, certificates, portfolio, and review stats.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            is_active=True, is_deleted=False, is_verified=True,
        )


@extend_schema(tags=['Profiles'])
class UserProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/

    Browse/search public user profiles. Supports search by name, location,
    bio, and filtering by availability.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['availability']
    search_fields = ['first_name', 'last_name', 'bio', 'location']
    ordering_fields = ['created_at', 'first_name']
    ordering = ['-created_at']

    def get_queryset(self):
        return User.objects.filter(
            is_active=True, is_deleted=False, is_verified=True,
        ).prefetch_related(
            'user_skills__skill__category',
            'experiences',
            'education_entries',
            'certificates',
            'portfolio_items',
            'reviews_received',
        )


@extend_schema(tags=['Profiles'])
class RecommendedProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/recommended/

    Get a curated list of recommended profiles for the dashboard.
    Returns 5 top profiles excluding the current user.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            is_active=True, is_deleted=False, is_verified=True,
        ).exclude(
            id=self.request.user.id
        ).order_by('-created_at')[:5]
