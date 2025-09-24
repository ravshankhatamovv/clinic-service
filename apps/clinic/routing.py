from django.urls import re_path
from .consumers import NurseNotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/nurse/(?P<user_id>\d+)/$", NurseNotificationConsumer.as_asgi()),
]
