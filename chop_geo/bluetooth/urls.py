from django.urls import path

from .views import (
    UserBluetoothStatisticsAPIView,
)

urlpatterns = [
    path('list/', UserBluetoothStatisticsAPIView.as_view(), name='bluetooth-list'),
]
