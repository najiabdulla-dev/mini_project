"""Django admin for Hiring."""
from django.contrib import admin
from .models import HireRequest


@admin.register(HireRequest)
class HireRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'provider', 'status', 'budget', 'deadline', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'client__email', 'provider__email']
    ordering = ['-created_at']
