"""
Helper utilities for Skill Swap.
"""

import random
import string
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)





def send_notification_email(email, subject, message):
    """
    Send a general notification email.

    Args:
        email: Recipient email address
        subject: Email subject
        message: Email body (plain text)
    """
    try:
        send_mail(
            subject=f'Skill Swap — {subject}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f'Failed to send notification email to {email}: {e}')
