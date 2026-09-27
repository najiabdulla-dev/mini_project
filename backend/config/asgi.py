"""
ASGI config for Skill Swap project.
Supports HTTP and WebSocket (for future Django Channels chat).
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.messaging.middleware import JWTAuthMiddlewareStack
import apps.messaging.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            apps.messaging.routing.websocket_urlpatterns
        )
    ),
})
