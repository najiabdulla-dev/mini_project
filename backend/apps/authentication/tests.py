"""
Tests for the authentication app.

Covers: registration, OTP verification, login, token refresh,
logout, forgot/reset password, change password, and profile endpoints.
"""

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import User, OTPCode
from .services import AuthService, OTPService


class UserModelTests(TestCase):
    """Tests for the User model."""

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='StrongP@ss1',
            first_name='Test',
            last_name='User',
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('StrongP@ss1'))
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_deleted)

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminP@ss1',
            first_name='Admin',
            last_name='User',
        )
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_verified)

    def test_create_user_without_email_raises(self):
        """Test that creating a user without email raises ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='StrongP@ss1',
                first_name='Test',
                last_name='User',
            )

    def test_soft_delete(self):
        """Test soft delete marks user as deleted without removing."""
        user = User.objects.create_user(
            email='delete@example.com',
            password='StrongP@ss1',
            first_name='Delete',
            last_name='Me',
        )
        user.soft_delete()
        self.assertTrue(user.is_deleted)
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.deleted_at)
        # User should still exist in database
        self.assertTrue(User.objects.filter(email='delete@example.com').exists())

    def test_restore_user(self):
        """Test restoring a soft-deleted user."""
        user = User.objects.create_user(
            email='restore@example.com',
            password='StrongP@ss1',
            first_name='Restore',
            last_name='Me',
        )
        user.soft_delete()
        user.restore()
        self.assertFalse(user.is_deleted)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.deleted_at)


class OTPModelTests(TestCase):
    """Tests for the OTPCode model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='otp@example.com',
            password='StrongP@ss1',
            first_name='OTP',
            last_name='User',
        )

    def test_create_otp(self):
        """Test creating an OTP code."""
        otp = OTPCode.create_otp(
            user=self.user,
            purpose=OTPCode.Purpose.EMAIL_VERIFICATION,
        )
        self.assertEqual(len(otp.code), 6)
        self.assertFalse(otp.is_used)
        self.assertTrue(otp.is_valid)

    def test_otp_expiry(self):
        """Test OTP expiration."""
        otp = OTPCode.create_otp(
            user=self.user,
            purpose=OTPCode.Purpose.EMAIL_VERIFICATION,
        )
        # Manually expire the OTP
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        self.assertTrue(otp.is_expired)
        self.assertFalse(otp.is_valid)

    def test_create_otp_invalidates_previous(self):
        """Test that creating a new OTP invalidates previous ones."""
        otp1 = OTPCode.create_otp(
            user=self.user,
            purpose=OTPCode.Purpose.EMAIL_VERIFICATION,
        )
        otp2 = OTPCode.create_otp(
            user=self.user,
            purpose=OTPCode.Purpose.EMAIL_VERIFICATION,
        )
        otp1.refresh_from_db()
        self.assertTrue(otp1.is_used)  # Previous OTP should be marked as used
        self.assertFalse(otp2.is_used)


class RegisterAPITests(TestCase):
    """Tests for the registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/register/'

    def test_register_success(self):
        """Test successful registration."""
        data = {
            'email': 'newuser@example.com',
            'password': 'StrongP@ss1',
            'password_confirm': 'StrongP@ss1',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_duplicate_email(self):
        """Test registration with existing email fails."""
        User.objects.create_user(
            email='existing@example.com',
            password='StrongP@ss1',
            first_name='Existing',
            last_name='User',
        )
        data = {
            'email': 'existing@example.com',
            'password': 'StrongP@ss1',
            'password_confirm': 'StrongP@ss1',
            'first_name': 'Duplicate',
            'last_name': 'User',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords fails."""
        data = {
            'email': 'mismatch@example.com',
            'password': 'StrongP@ss1',
            'password_confirm': 'DifferentP@ss1',
            'first_name': 'Mismatch',
            'last_name': 'User',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        """Test registration with weak password fails."""
        data = {
            'email': 'weak@example.com',
            'password': '12345',
            'password_confirm': '12345',
            'first_name': 'Weak',
            'last_name': 'Pass',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VerifyOTPAPITests(TestCase):
    """Tests for OTP verification endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/verify-otp/'
        self.user = User.objects.create_user(
            email='verify@example.com',
            password='StrongP@ss1',
            first_name='Verify',
            last_name='User',
            is_verified=False,
        )
        self.otp = OTPCode.create_otp(
            user=self.user,
            purpose=OTPCode.Purpose.EMAIL_VERIFICATION,
        )

    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        data = {'email': 'verify@example.com', 'code': self.otp.code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_verify_otp_invalid_code(self):
        """Test verification with wrong code fails."""
        data = {'email': 'verify@example.com', 'code': '000000'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_expired(self):
        """Test verification with expired code fails."""
        self.otp.expires_at = timezone.now() - timedelta(minutes=1)
        self.otp.save()
        data = {'email': 'verify@example.com', 'code': self.otp.code}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITests(TestCase):
    """Tests for the login endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/login/'
        self.user = User.objects.create_user(
            email='login@example.com',
            password='StrongP@ss1',
            first_name='Login',
            last_name='User',
            is_verified=True,
        )

    def test_login_success(self):
        """Test successful login returns tokens and user data."""
        data = {'email': 'login@example.com', 'password': 'StrongP@ss1'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertIn('user', response.data['data'])

    def test_login_wrong_password(self):
        """Test login with wrong password fails."""
        data = {'email': 'login@example.com', 'password': 'WrongP@ss1'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unverified_email(self):
        """Test login with unverified email fails."""
        self.user.is_verified = False
        self.user.save()
        data = {'email': 'login@example.com', 'password': 'StrongP@ss1'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogoutAPITests(TestCase):
    """Tests for the logout endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='logout@example.com',
            password='StrongP@ss1',
            first_name='Logout',
            last_name='User',
            is_verified=True,
        )
        # Login to get tokens
        login_response = self.client.post(
            '/api/auth/login/',
            {'email': 'logout@example.com', 'password': 'StrongP@ss1'},
            format='json',
        )
        self.access_token = login_response.data['data']['access']
        self.refresh_token = login_response.data['data']['refresh']

    def test_logout_success(self):
        """Test successful logout blacklists refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            '/api/auth/logout/',
            {'refresh': self.refresh_token},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MeAPITests(TestCase):
    """Tests for the /me/ profile endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='me@example.com',
            password='StrongP@ss1',
            first_name='Me',
            last_name='User',
            is_verified=True,
        )
        login_response = self.client.post(
            '/api/auth/login/',
            {'email': 'me@example.com', 'password': 'StrongP@ss1'},
            format='json',
        )
        self.access_token = login_response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_profile(self):
        """Test getting current user profile."""
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'me@example.com')

    def test_update_profile(self):
        """Test updating user profile."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Hello, I am a skill swapper!',
            'location': 'Mumbai, India',
        }
        response = self.client.patch('/api/auth/me/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.bio, 'Hello, I am a skill swapper!')

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access /me/."""
        self.client.credentials()  # Remove auth
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordAPITests(TestCase):
    """Tests for the change-password endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='changepw@example.com',
            password='StrongP@ss1',
            first_name='Change',
            last_name='Password',
            is_verified=True,
        )
        login_response = self.client.post(
            '/api/auth/login/',
            {'email': 'changepw@example.com', 'password': 'StrongP@ss1'},
            format='json',
        )
        self.access_token = login_response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_change_password_success(self):
        """Test successful password change."""
        data = {
            'old_password': 'StrongP@ss1',
            'new_password': 'NewStrong@P2',
            'new_password_confirm': 'NewStrong@P2',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrong@P2'))

    def test_change_password_wrong_old(self):
        """Test change password with wrong old password fails."""
        data = {
            'old_password': 'WrongOldP@ss1',
            'new_password': 'NewStrong@P2',
            'new_password_confirm': 'NewStrong@P2',
        }
        response = self.client.post('/api/auth/change-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
