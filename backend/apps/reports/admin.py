"""Django admin for Reports."""
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported_user', 'type', 'status', 'created_at', 'resolved_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['reporter__email', 'reported_user__email', 'reason']
    ordering = ['-created_at']
