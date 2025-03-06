from django.urls import path

from .views import (
    UserBluetoothStatisticsAPIView,
    BluetoothStatisticsAPIView
)

urlpatterns = [
    path('list/', UserBluetoothStatisticsAPIView.as_view(), name='bluetooth-list'),
    path('total-count/', BluetoothStatisticsAPIView.as_view(), name='bluetooth-total-count'),
]
