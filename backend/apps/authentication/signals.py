"""
Signal handlers for the authentication app.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# Note: OTP sending is handled in AuthService.register_user(),
# not via signals, to keep the flow explicit and testable.
# Signals here are for side-effects like logging.
