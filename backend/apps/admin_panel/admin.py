"""Django admin for Admin Panel."""
from django.contrib import admin
from .models import AdminSettings


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']
    ordering = ['key']
