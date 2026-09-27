from rest_framework import serializers
from apps.reports.models import Report

class AdminReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.EmailField(source='reporter.email', read_only=True)
    reported_user_email = serializers.EmailField(source='reported_user.email', read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'reporter_email', 'reported_user_email', 'reason', 'status', 'created_at']
        read_only_fields = fields
