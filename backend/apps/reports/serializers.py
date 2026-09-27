from rest_framework import serializers
from .models import Report

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'reported_user', 'reason', 'type', 'status', 'created_at']
        read_only_fields = ['id', 'type', 'status', 'created_at']

    def create(self, validated_data):
        # Automatically set the reporter to the logged-in user
        validated_data['reporter'] = self.context['request'].user
        validated_data['type'] = Report.Type.USER
        validated_data['status'] = Report.Status.PENDING
        return super().create(validated_data)
