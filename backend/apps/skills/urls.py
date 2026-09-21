"""
Skill URL routes for Skill Swap.
All endpoints are prefixed with /api/skills/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'skills'

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('', views.SkillViewSet, basename='skill')

urlpatterns = [
    path('', include(router.urls)),
]
