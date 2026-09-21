"""
ASGI config for Skill Swap project.
Supports HTTP and WebSocket (for future Django Channels chat).
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_asgi_application()
