from django.contrib.gis.db.models.functions import Length
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

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


class TopDriversView(APIView):

    def get_top_drivers(self, start_date):
        """
        Возвращает ТОП-5 водителей по пройденной дистанции с указанной даты.
        """
        top_drivers = (
            VehicleTrajectoryRoute.objects
            .filter(start_time__gte=start_date)
            .annotate(total_distance=Length('trajectory'))  # Вычисляем длину маршрута
            .values('vehicle')
            .annotate(total_distance=Sum('total_distance'))  # Суммируем расстояния
            .order_by('-total_distance')[:5]  # ТОП-5
        )

        # Получаем данные о водителях
        vehicle_ids = [driver['vehicle'] for driver in top_drivers]
        vehicles = Vehicle.objects.filter(id__in=vehicle_ids)
        vehicle_data = VehicleSerializer(vehicles, many=True).data

        # Добавляем дистанцию
        for vehicle in vehicle_data:
            vehicle_id = vehicle['id']
            vehicle['total_distance'] = next(
                (d['total_distance'] for d in top_drivers if d['vehicle'] == vehicle_id), 0
            )

        return vehicle_data

    def get(self, request, period):
        """
        GET-запрос для получения ТОП-5 водителей по пройденной дистанции.
        Параметры: period (day, week, month)
        """
        today = now().date()

        if period == 'day':
            start_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        else:
            return Response({"error": "Invalid period. Use 'day', 'week', or 'month'."}, status=400)

        top_drivers = self.get_top_drivers(start_date)
        return Response({"period": period, "top_drivers": top_drivers})
