"""
Input validators for Skill Swap.
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_phone_number(value):
    """
    Validate phone number format.
    Accepts: +1234567890, 1234567890, +91-9876543210
    """
    pattern = r'^\+?[\d\-\s]{7,15}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Enter a valid phone number (7-15 digits, optional + prefix).'
        )


def validate_github_url(value):
    """Validate that the URL is a GitHub profile URL."""
    if value and not re.match(r'^https?://(www\.)?github\.com/[\w\-]+/?$', value):
        raise ValidationError(
            'Enter a valid GitHub profile URL (e.g., https://github.com/username).'
        )


def validate_linkedin_url(value):
    """Validate that the URL is a LinkedIn profile URL."""
    if value and not re.match(r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$', value):
        raise ValidationError(
            'Enter a valid LinkedIn profile URL (e.g., https://linkedin.com/in/username).'
        )


def validate_rating(value):
    """Validate rating is between 1 and 5."""
    if not (1 <= value <= 5):
        raise ValidationError('Rating must be between 1 and 5.')


def validate_hourly_rate(value):
    """Validate hourly rate is positive and reasonable."""
    if value is not None and value < 0:
        raise ValidationError('Hourly rate cannot be negative.')
    if value is not None and value > 10000:
        raise ValidationError('Hourly rate cannot exceed 10,000.')


def validate_password_strength(password):
    """
    Custom password strength validator.
    Requirements: min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char.
    """
    errors = []

    if len(password) < 8:
        errors.append('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character.')

    if errors:
        raise ValidationError(errors)
