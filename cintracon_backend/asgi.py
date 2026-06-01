import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cintracon_backend.settings')

# Must be called before importing routing/middleware to ensure Django is ready
django_asgi_app = get_asgi_application()

from notifications.routing import websocket_urlpatterns  # noqa: E402
from cintracon_backend.middleware import JWTAuthMiddleware  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
})
