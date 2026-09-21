"""
Notification URL routes for Skill Swap.
All endpoints are prefixed with /api/notifications/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'notifications'

router = DefaultRouter()
router.register('', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
