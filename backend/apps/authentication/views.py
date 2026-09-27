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
from .utils import generate_and_send_otp
from .models import EmailOTP
from django.utils import timezone
from django.db import transaction
import smtplib

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
        email = request.data.get('email', '').lower()
        if email:
            # If user exists but is not verified, delete them so they can retry registration
            unverified_user = User.objects.filter(email=email, is_email_verified=False).first()
            if unverified_user:
                unverified_user.delete()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                user = serializer.save()
                generate_and_send_otp(user)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error during registration: {e}")
            return Response(
                {
                    'success': False,
                    'message': 'Failed to send verification email. Please check the email server configuration.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Unexpected error during registration: {e}\n{tb}")
            return Response(
                {
                    'success': False,
                    'message': f"Internal Server Error during registration: {type(e).__name__} - {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                'success': True,
                'message': 'Registration successful. Please check your email for verification code.',
                'email': user.email
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


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/
    
    Verifies the email OTP.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'login'

    @extend_schema(tags=['Authentication'])
    def post(self, request):
        email = request.data.get('email', '').lower()
        otp_code = request.data.get('otp', '')

        if not email or not otp_code:
            return Response({'success': False, 'message': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_email_verified:
            return Response({'success': True, 'message': 'Email already verified.'}, status=status.HTTP_200_OK)

        # Get latest unexpired unused OTP
        otp_record = EmailOTP.objects.filter(
            user=user, 
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()

        if not otp_record:
            return Response({'success': False, 'message': 'Invalid or expired OTP code.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.otp_code != otp_code:
            otp_record.attempts += 1
            if otp_record.attempts >= 5:
                otp_record.is_used = True
            otp_record.save(update_fields=['attempts', 'is_used'])
            return Response({'success': False, 'message': f'Invalid code. {5 - otp_record.attempts} attempts remaining.'}, status=status.HTTP_400_BAD_REQUEST)

        # Success
        otp_record.is_used = True
        otp_record.save(update_fields=['is_used'])
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified', 'updated_at'])

        return Response({'success': True, 'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    POST /api/auth/resend-otp/
    
    Resends the email OTP if cooldown has passed.
    """
    permission_classes = [AllowAny]
    throttle_scope = 'login'

    @extend_schema(tags=['Authentication'])
    def post(self, request):
        email = request.data.get('email', '').lower()

        if not email:
            return Response({'success': False, 'message': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_email_verified:
            return Response({'success': False, 'message': 'Account already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check cooldown (60 seconds)
        last_otp = EmailOTP.objects.filter(user=user).first()
        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < 60:
            return Response({'success': False, 'message': 'Please wait 60 seconds before requesting a new OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            generate_and_send_otp(user)
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error during resend: {e}")
            return Response({'success': False, 'message': 'Failed to send verification email. Please check email configuration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error during resend: {e}")
            return Response({'success': False, 'message': f'Internal Server Error: {type(e).__name__} - {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': True, 'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)

