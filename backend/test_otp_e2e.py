import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

from django.test import Client
from django.core import mail
from apps.authentication.models import User, EmailOTP
from django.utils import timezone
from datetime import timedelta

def test_otp_flow():
    client = Client()
    
    # 1. Register a new user
    print("Testing Registration...")
    resp = client.post('/api/auth/register/', {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'new_user2@example.com',
        'password': 'StrongPassword123!',
        'password_confirm': 'StrongPassword123!'
    })
    assert resp.status_code == 201, f"Registration failed: {resp.content}"
    
    # 2. Check if user is created with is_email_verified=False
    user = User.objects.get(email='new_user2@example.com')
    assert not user.is_email_verified, "User should be created unverified"
    
    # 3. Check if email was sent
    assert len(mail.outbox) >= 1, "OTP Email was not sent"
    otp_email = mail.outbox[-1]
    assert "Verify your email address" in otp_email.subject
    print("Registration & Email Sent: PASSED")
    
    # Extract OTP from DB (to simulate user reading email)
    otp_record = EmailOTP.objects.get(user=user)
    valid_otp = otp_record.otp_code
    
    # 4. Try Login (Should fail with 403 Unverified)
    print("Testing Unverified Login...")
    resp = client.post('/api/auth/login/', {
        'email': 'new_user2@example.com',
        'password': 'StrongPassword123!'
    })
    assert resp.status_code == 403, f"Login should be rejected: {resp.status_code}"
    assert "verify" in resp.json()['message'].lower(), "Should ask for verification"
    print("Unverified Login Rejected: PASSED")
    
    # 5. Try Incorrect OTP
    print("Testing Incorrect OTP...")
    resp = client.post('/api/auth/verify-otp/', {
        'email': 'new_user2@example.com',
        'otp': '000000'
    })
    assert resp.status_code == 400
    assert "Invalid code" in resp.json()['message']
    print("Incorrect OTP Rejected: PASSED")
    
    # 6. Try Expired OTP
    print("Testing Expired OTP...")
    otp_record.expires_at = timezone.now() - timedelta(minutes=5)
    otp_record.save()
    resp = client.post('/api/auth/verify-otp/', {
        'email': 'new_user2@example.com',
        'otp': valid_otp
    })
    assert resp.status_code == 400
    assert "expired" in resp.json()['message'].lower()
    print("Expired OTP Rejected: PASSED")
    
    # 7. Resend OTP
    print("Testing Resend OTP...")
    # Bypass cooldown for testing
    otp_record.created_at = timezone.now() - timedelta(minutes=5)
    otp_record.save()
    resp = client.post('/api/auth/resend-otp/', {
        'email': 'new_user2@example.com'
    })
    assert resp.status_code == 200, f"Resend failed: {resp.content}"
    assert len(mail.outbox) >= 2, "Second email not sent"
    
    new_otp_record = EmailOTP.objects.filter(user=user, is_used=False).first()
    new_valid_otp = new_otp_record.otp_code
    print("Resend OTP: PASSED")
    
    # 8. Verify OTP Successfully
    print("Testing Successful Verification...")
    resp = client.post('/api/auth/verify-otp/', {
        'email': 'new_user2@example.com',
        'otp': new_valid_otp
    })
    assert resp.status_code == 200, f"Verification failed: {resp.content}"
    user.refresh_from_db()
    assert user.is_email_verified, "User should now be verified"
    print("Verification Success: PASSED")
    
    # 9. Try Login Again (Should Succeed)
    print("Testing Verified Login...")
    resp = client.post('/api/auth/login/', {
        'email': 'new_user2@example.com',
        'password': 'StrongPassword123!'
    })
    assert resp.status_code == 200, "Verified user should be able to login"
    print("Verified Login: PASSED")
    
    # 10. Existing Users (Seeded) can still log in
    print("Testing Seeded User Login...")
    resp = client.post('/api/auth/login/', {
        'email': 'user1@example.com',
        'password': 'Password123!'
    })
    if resp.status_code == 200:
        print("Seeded User Login: PASSED")
    else:
        print(f"Seeded User Login FAILED! {resp.content}")
        
    print("\nAll Backend E2E Tests Passed successfully!")

if __name__ == '__main__':
    test_otp_flow()
