import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import apps.clinic.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket':  
        AuthMiddlewareStack(URLRouter(
            apps.clinic.routing.websocket_urlpatterns
        ),
        )
})