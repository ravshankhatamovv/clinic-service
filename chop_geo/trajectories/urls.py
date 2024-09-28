from django.urls import path
from .views import VehicleTrajectoryCreateAPIView, BulkVehicleTrajectoryCreateAPIView
from .views import DriverListView, DriverDetailView, DriverPointsListView, DriverRoutesListView


urlpatterns = [
    path('create/', VehicleTrajectoryCreateAPIView.as_view(), name='vehicletrajectory-create'),
    path('bulk-create/', BulkVehicleTrajectoryCreateAPIView.as_view(), name='bulk-vehicletrajectory-create'),

    path('driver-list/', DriverListView.as_view(), name='driver-list'),
    path('driver-detail/<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
    path('driver-points/list/<int:vehicle_id>/', DriverPointsListView.as_view(), name='driver-points-list'),
    path('driver-routes/list/<int:vehicle_id>/', DriverRoutesListView.as_view(), name='driver-routes-list'),
]
