from django.urls import path
from .views import UserTrajectoryCreateAPIView, BulkVehicleTrajectoryCreateAPIView, TopDriversView


urlpatterns = [
    path('create/', UserTrajectoryCreateAPIView.as_view(), name='vehicletrajectory-create'),
    path('bulk-create/', BulkVehicleTrajectoryCreateAPIView.as_view(), name='bulk-vehicletrajectory-create'),
    path('top-drivers/<str:period>/', TopDriversView.as_view(), name='top-drivers'),
]
