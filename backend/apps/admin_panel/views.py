from rest_framework import generics, filters
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from apps.reports.models import Report
from apps.authentication.serializers import UserSerializer
from .serializers import AdminReportSerializer

User = get_user_model()

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

class AdminReportListView(generics.ListAPIView):
    """
    GET /api/admin-panel/reports/
    """
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = AdminReportSerializer
    permission_classes = [IsAdminUser]

class AdminUserListView(generics.ListAPIView):
    """
    GET /api/admin-panel/users/
    """
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email']

class AdminUserDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/admin-panel/users/<id>/
    """
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    
    def perform_destroy(self, instance):
        if instance.is_admin and instance.id == self.request.user.id:
            raise PermissionDenied("You cannot delete your own admin account.")
        instance.delete()
