from rest_framework import viewsets, generics, permissions
from .models import VehicleTrajectoryRoute, VehicleTrajectory, Vehicle
from .serializers import (
    VehicleTrajectoryRouteSerializer, VehicleTrajectorySerializer,
    VehicleTrajectoryCreateSerializer, VehicleSerializer, VehicleDetailSerializer
)


class VehicleTrajectoryRouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VehicleTrajectoryRoute.objects.all()
    serializer_class = VehicleTrajectoryRouteSerializer


class VehicleTrajectoryCreateAPIView(generics.CreateAPIView):
    queryset = VehicleTrajectory.objects.all()
    serializer_class = VehicleTrajectorySerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can create trajectories

    def perform_create(self, serializer):
        # Automatically associate the VehicleTrajectory with the Vehicle of the current user
        try:
            vehicle = self.request.user.vehicle
        except Vehicle.DoesNotExist:
            vehicle = Vehicle.objects.create(user=self.request.user)
        serializer.save(vehicle=vehicle)


class BulkVehicleTrajectoryCreateAPIView(generics.CreateAPIView):
    queryset = VehicleTrajectory.objects.all()
    serializer_class = VehicleTrajectoryCreateSerializer

    def perform_create(self, serializer):
        try:
            vehicle = self.request.user.vehicle
        except Vehicle.DoesNotExist:
            vehicle = Vehicle.objects.create(user=self.request.user)
        # Additional logic to prevent multiple objects creation
        serializer.save(vehicle=vehicle)


class DriverListView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class DriverDetailView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleDetailSerializer
    lookup_field = 'pk'  # можно использовать 'guid', если это основной идентификатор


class DriverPointsListView(generics.ListAPIView):
    serializer_class = VehicleTrajectorySerializer

    def get_queryset(self):
        vehicle_id = self.kwargs['vehicle_id']
        return VehicleTrajectory.objects.filter(vehicle_id=vehicle_id)


class DriverRoutesListView(generics.ListAPIView):
    serializer_class = VehicleTrajectoryRouteSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs['vehicle_id']
        return VehicleTrajectoryRoute.objects.filter(vehicle_id=vehicle_id)
