"""
Messaging URL routes for Skill Swap.
All endpoints are prefixed with /api/messages/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'messaging'

router = DefaultRouter()
router.register('', views.MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
