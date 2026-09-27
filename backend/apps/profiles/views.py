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
from .models import RecommendationHistory
from . import ai_utils


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
            is_active=True, is_deleted=False, is_email_verified=True,
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
            is_active=True, is_deleted=False, is_email_verified=True,
        ).exclude(
            id=self.request.user.id
        ).exclude(
            is_admin=True
        ).exclude(
            is_staff=True
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

    Get a curated list of recommended profiles for the dashboard using
    AI-based content recommendation (sentence embeddings + cosine similarity).
    Returns 5 top profiles excluding the current user.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Case, When
        from django.utils import timezone
        
        current_user = self.request.user
        
        # 1. Fetch all eligible candidate profiles
        candidates = list(User.objects.filter(
            is_active=True, is_deleted=False, is_email_verified=True,
        ).exclude(
            id=current_user.id
        ).exclude(
            is_admin=True
        ).exclude(
            is_staff=True
        ).prefetch_related('user_skills'))
        
        if not candidates:
            return User.objects.none()
            
        # 2. Compute AI Similarity using pre-generated sentence embeddings
        current_embedding = current_user.profile_embedding
        if not current_embedding:
            # Fallback if current user has no embedding generated yet
            ai_utils.update_user_embedding(current_user)
            current_user.refresh_from_db()
            current_embedding = current_user.profile_embedding
            
        # Fetch recommendation history for the rotation factor
        # Get count of times each user was recommended to current user
        history = RecommendationHistory.objects.filter(viewer=current_user).values_list('shown_user_id', flat=True)
        exposure_counts = {}
        for uid in history:
            exposure_counts[uid] = exposure_counts.get(uid, 0) + 1
            
        scored_candidates = []
        for candidate in candidates:
            candidate_embedding = candidate.profile_embedding
            similarity_score = 0
            if candidate_embedding and current_embedding:
                similarity_score = ai_utils.cosine_similarity(current_embedding, candidate_embedding)
                
            # Rotation factor: Heavily penalize users who have been shown frequently
            # so that everyone gets shown eventually.
            times_shown = exposure_counts.get(candidate.id, 0)
            rotation_penalty = times_shown * 0.5  # Reduces score significantly per view
            
            # Combine AI similarity score and rotation penalty
            final_score = similarity_score - rotation_penalty
            scored_candidates.append((final_score, candidate))
            
        # 3. Sort by highest score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # 4. Extract top 5
        top_candidates = [candidate for score, candidate in scored_candidates[:5]]
        top_ids = [c.id for c in top_candidates]
        
        if not top_ids:
            return User.objects.none()
            
        # 5. Log them as shown in the tracking table
        now = timezone.now()
        history_records = [
            RecommendationHistory(viewer=current_user, shown_user_id=cid, shown_at=now)
            for cid in top_ids
        ]
        RecommendationHistory.objects.bulk_create(history_records)
            
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(top_ids)])
        return User.objects.filter(pk__in=top_ids).order_by(preserved)
