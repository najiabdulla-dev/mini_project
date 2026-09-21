"""
Hiring URL routes for Skill Swap.
All endpoints are prefixed with /api/hiring/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'hiring'

router = DefaultRouter()
router.register('', views.HireRequestViewSet, basename='hire-request')

urlpatterns = [
    path('', include(router.urls)),
]
