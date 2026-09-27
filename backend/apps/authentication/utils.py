import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP

def generate_and_send_otp(user):
    # Invalidate previous unexpired OTPs
    EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Generate 6-digit secure numerical code
    otp_code = f"{secrets.randbelow(1000000):06d}"
    
    # Save OTP
    expiry_minutes = int(getattr(settings, 'OTP_EXPIRY_MINUTES', 10))
    EmailOTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=timezone.now() + timedelta(minutes=expiry_minutes)
    )
    
    # Send Email
    subject = "Verify your email address for HireHub"
    message = f"Hello {user.first_name},\n\nYour verification code is: {otp_code}\n\nThis code will expire in {expiry_minutes} minutes.\n\nThank you,\nThe HireHub Team"
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
