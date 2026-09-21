"""
Profile URL routes for Skill Swap.
All endpoints are prefixed with /api/profiles/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'profiles'

router = DefaultRouter()
router.register('my/skills', views.UserSkillViewSet, basename='my-skill')
router.register('my/experiences', views.ExperienceViewSet, basename='my-experience')
router.register('my/education', views.EducationViewSet, basename='my-education')
router.register('my/certificates', views.CertificateViewSet, basename='my-certificate')
router.register('my/portfolio', views.PortfolioViewSet, basename='my-portfolio')

urlpatterns = [
    # Public profile browsing
    path('', views.UserProfileListView.as_view(), name='profile-list'),
    path('recommended/', views.RecommendedProfileListView.as_view(), name='profile-recommended'),
    path('<int:pk>/', views.UserProfileView.as_view(), name='profile-detail'),

    # Current user's profile sub-resources
    path('', include(router.urls)),
]
