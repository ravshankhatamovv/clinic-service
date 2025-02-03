from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import Length
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from chop_geo.users.serializers import UserSerializer
from .models import Vehicle, UserTrajectory, UserTrajectoryRoute
from .serializers import (
    UserTrajectorySerializer,
    VehicleTrajectoryCreateSerializer
)

User = get_user_model()


class UserTrajectoryCreateAPIView(generics.CreateAPIView):
    queryset = UserTrajectory.objects.all()
    serializer_class = UserTrajectorySerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can create trajectories

    def perform_create(self, serializer):
        # Automatically associate the VehicleTrajectory with the Vehicle of the current user
        try:
            vehicle = self.request.user.vehicle
        except Vehicle.DoesNotExist:
            vehicle = Vehicle.objects.create(user=self.request.user)
        serializer.save(vehicle=vehicle)


class BulkVehicleTrajectoryCreateAPIView(generics.CreateAPIView):
    queryset = UserTrajectory.objects.all()
    serializer_class = VehicleTrajectoryCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        # Additional logic to prevent multiple objects creation
        serializer.save(user=user)


class TopDriversView(APIView):
    permission_classes = [AllowAny]

    def get_top_drivers(self, start_date):
        """
        Возвращает ТОП-5 водителей по пройденной дистанции с указанной даты.
        Только те, у которых имеется driver_uuid в модели User
        """
        top_drivers = (
            UserTrajectoryRoute.objects
            .filter(start_time__gte=start_date)
            .annotate(total_distance=Length('trajectory'))  # Вычисляем длину маршрута
            .values('user')
            .annotate(total_distance=Sum('total_distance'))  # Суммируем расстояния
            .order_by('-total_distance')[:5]  # ТОП-5
        )

        # Получаем данные о водителях
        vehicle_ids = [driver['user'] for driver in top_drivers]
        vehicles = User.objects.filter(id__in=vehicle_ids)
        vehicle_data = UserSerializer(vehicles, many=True).data

        # Добавляем дистанцию
        for vehicle in vehicle_data:
            user = vehicle['id']
            vehicle['total_distance'] = next(
                (d['total_distance'] for d in top_drivers if d['user'] == user), 0
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
