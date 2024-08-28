from django.urls import path
from .views import VehicleTrajectoryCreateAPIView, BulkVehicleTrajectoryCreateAPIView

urlpatterns = [
    path('create/', VehicleTrajectoryCreateAPIView.as_view(), name='vehicletrajectory-create'),
    path('bulk-create/', BulkVehicleTrajectoryCreateAPIView.as_view(), name='bulk-vehicletrajectory-create'),
]
