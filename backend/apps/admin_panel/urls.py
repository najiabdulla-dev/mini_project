from django.urls import path
from .views import AdminReportListView, AdminUserDeleteView, AdminUserListView

app_name = 'admin_panel'

urlpatterns = [
    path('reports/', AdminReportListView.as_view(), name='admin_reports'),
    path('users/', AdminUserListView.as_view(), name='admin_users'),
    path('users/<int:pk>/', AdminUserDeleteView.as_view(), name='admin_user_delete'),
]
