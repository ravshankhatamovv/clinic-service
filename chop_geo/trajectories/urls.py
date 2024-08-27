from django.urls import path
from .views import VehicleTrajectoryCreateAPIView

urlpatterns = [
    path('create/', VehicleTrajectoryCreateAPIView.as_view(), name='vehicletrajectory-create'),
]
