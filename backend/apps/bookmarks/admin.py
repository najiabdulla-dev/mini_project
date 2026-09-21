"""Django admin for Bookmarks."""
from django.contrib import admin
from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'bookmarked_user', 'created_at']
    search_fields = ['user__email', 'bookmarked_user__email']
    ordering = ['-created_at']
