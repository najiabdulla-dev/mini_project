"""Django admin for Reviews."""
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'rating', 'is_reported', 'hire_request', 'created_at']
    list_filter = ['rating', 'is_reported', 'created_at']
    search_fields = ['reviewer__email', 'reviewee__email', 'comment']
    ordering = ['-created_at']
