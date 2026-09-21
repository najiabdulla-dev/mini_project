"""
Bookmark URL routes for Skill Swap.
All endpoints are prefixed with /api/bookmarks/ (configured in config/urls.py).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'bookmarks'

router = DefaultRouter()
router.register('', views.BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('', include(router.urls)),
]
