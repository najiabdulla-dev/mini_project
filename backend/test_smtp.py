import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_smtp():
    print(f"Using EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"Using EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"Using EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    
    try:
        sent = send_mail(
            subject="Test SMTP from HireHub",
            message="If you receive this, SMTP is working correctly!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER], # send to self
            fail_silently=False,
        )
        print(f"Success! {sent} email(s) sent.")
    except Exception as e:
        print(f"Failed to send email: {type(e).__name__} - {str(e)}")

if __name__ == '__main__':
    test_smtp()
