"""
Authentication views for Skill Swap.

All auth endpoints with rate limiting applied to sensitive operations.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(CreateAPIView):
    """
    POST /api/auth/register/
    
    Register a new user with email and password.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    throttle_scope = 'login'

    @extend_schema(
        responses={201: OpenApiResponse(description='User registered successfully')},
        tags=['Authentication'],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Registration successful.',
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    
    Login with email and password to get JWT tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = 'login'

    @extend_schema(
        responses={200: OpenApiResponse(description='Login successful with tokens and user data')},
        tags=['Authentication'],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(
            {
                'success': True,
                'message': 'Login successful.',
                'data': {
                    'refresh': serializer.validated_data['refresh'],
                    'access': serializer.validated_data['access'],
                    'user': serializer.validated_data['user'],
                },
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    
    Logout and blacklist the refresh token.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description='Successfully logged out')},
        tags=['Authentication'],
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'success': True, 'message': 'Logged out successfully.'})
        except Exception as e:
            return Response(
                {'success': False, 'message': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(RetrieveUpdateAPIView):
    """
    GET  /api/auth/me/  — Get current user profile
    PUT  /api/auth/me/  — Update current user profile
    PATCH /api/auth/me/ — Partial update current user profile
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    @extend_schema(
        responses={200: UserSerializer},
        tags=['Authentication'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['Authentication'],
    )
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        # Return full user data after update
        user_data = UserSerializer(self.get_object()).data
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'data': user_data,
        })

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['Authentication'],
    )
    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        user_data = UserSerializer(self.get_object()).data
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'data': user_data,
        })
