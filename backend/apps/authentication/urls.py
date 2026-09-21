"""
Authentication URL routes for Skill Swap.
All endpoints are prefixed with /api/auth/ (configured in config/urls.py).
"""

from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Profile
    path('me/', views.MeView.as_view(), name='me'),
]
