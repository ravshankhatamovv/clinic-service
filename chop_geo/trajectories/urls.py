from django.urls import path

from .views import (
    BulkVehicleTrajectoryCreateAPIView,
    TopDriversView,
    UserTrajectoryRouteRetrieveAPIView,
    UserHeatmapAPIView
)

urlpatterns = [
    # path('create/', UserTrajectoryCreateAPIView.as_view(), name='vehicletrajectory-create'),
    path('bulk-create/', BulkVehicleTrajectoryCreateAPIView.as_view(), name='bulk-vehicletrajectory-create'),
    path('top-drivers/<str:period>/', TopDriversView.as_view(), name='top-drivers'),
    path('heatmap/', UserHeatmapAPIView.as_view(), name='heatmap-list'),
    path("user-routes/",
         UserTrajectoryRouteRetrieveAPIView.as_view(), name="user-routes-retrieve"),
]
