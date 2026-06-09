"""
ASGI config for Wateen project.

It exposes the ASGI callable as a module-level variable named ``application``.
Handles both HTTP and WebSocket protocols via Django Channels.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import sys

# Ensure backend root is on the path so that config, users, etc. are importable
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early to populate AppRegistry.
# This MUST happen before importing any models or consumers.
django_asgi_app = get_asgi_application()

# Import after Django setup to avoid AppRegistryNotReady
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from config.middleware import JWTAuthMiddleware  # noqa: E402
from visits.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
