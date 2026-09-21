"""
Review URL routes for Skill Swap.
All endpoints are prefixed with /api/reviews/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

router = DefaultRouter()
router.register('', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
