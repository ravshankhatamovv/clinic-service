from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import Length
from django.db.models import Sum, Q
from django.utils.timezone import make_aware
from django.utils.timezone import now, timedelta
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Count
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


from chop_geo.users.serializers import UserSerializer
from .models import UserTrajectory, UserTrajectoryRoute
from .serializers import (
    VehicleTrajectoryCreateSerializer,
    UserTrajectoryRouteSerializer
)

User = get_user_model()


#
# class UserTrajectoryCreateAPIView(generics.CreateAPIView):
#     queryset = UserTrajectory.objects.all()
#     serializer_class = UserTrajectorySerializer
#     permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can create trajectories
#
#     def perform_create(self, serializer):
#         # Automatically associate the VehicleTrajectory with the Vehicle of the current user
#         try:
#             vehicle = self.request.user.vehicle
#         except User.DoesNotExist:
#             vehicle = Vehicle.objects.create(user=self.request.user)
#         serializer.save(vehicle=vehicle)


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
            .filter(start_time__gte=start_date, user__driver_guid__isnull=False)
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


class UserTrajectoryRouteRetrieveAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "lead_ids": {"type": "array", "items": {"type": "string"}},
                    "driver_ids": {"type": "array", "items": {"type": "string"}},
                    "day": {"type": "string", "format": "date", "example": "2025-02-12"},
                    "month": {"type": "string", "format": "yyyy-MM", "example": "2025-02"},
                    "weekly": {"type": "string", "format": "date", "example": "2025-02-12"},
                    "time": {"type": "string", "format": "HH:MM", "example": "15:00"},
                    "duration_minutes": {"type": "integer", "example": 15}
                },
                "required": ["lead_ids", "driver_ids"]
            }
        },
        # responses={200: UserTrajectoryRouteSerializer(many=True)},
    )
    def post(self, request, *args, **kwargs):
        lead_ids = request.data.get("lead_ids", [])
        driver_ids = request.data.get("driver_ids", [])

        if not isinstance(lead_ids, list) or not isinstance(driver_ids, list) or (not lead_ids and not driver_ids):
            return Response({"error": "Invalid or missing lead_ids and driver_ids lists"}, status=status.HTTP_400_BAD_REQUEST)

        user_filter = Q()
        if lead_ids:
            user_filter |= Q(guid__in=lead_ids)
        if driver_ids:
            user_filter |= Q(driver_guid__in=driver_ids)

        queryset = UserTrajectoryRoute.objects.filter(user__in=User.objects.filter(user_filter))

        day = request.data.get("day")
        month = request.data.get("month")
        weekly = request.data.get("weekly")
        time = request.data.get("time")  # HH:MM format
        duration_minutes = request.data.get("duration_minutes", 15)

        if day:
            try:
                day_date = make_aware(datetime.strptime(day, "%Y-%m-%d"))
                queryset = queryset.filter(
                    Q(start_time__date=day_date.date()) | Q(end_time__date=day_date.date())
                )
            except ValueError:
                return Response({"error": "Invalid date format for 'day'. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

            if time:
                try:
                    time_obj = datetime.strptime(time, "%H:%M").time()
                    filter_start_time = make_aware(datetime.combine(day_date.date(), time_obj))
                    filter_end_time = filter_start_time + timedelta(minutes=int(duration_minutes))

                    queryset = queryset.filter(
                        Q(start_time__range=[filter_start_time, filter_end_time]) |
                        Q(end_time__range=[filter_start_time, filter_end_time])
                    )
                except ValueError:
                    return Response({"error": "Invalid time format for 'time'. Use HH:MM."}, status=status.HTTP_400_BAD_REQUEST)

        elif month:
            try:
                month_date = make_aware(datetime.strptime(month, "%Y-%m"))
                queryset = queryset.filter(
                    Q(start_time__year=month_date.year, start_time__month=month_date.month) |
                    Q(end_time__year=month_date.year, end_time__month=month_date.month)
                )
            except ValueError:
                return Response({"error": "Invalid date format for 'month'. Use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)

        elif weekly:
            try:
                week_date = make_aware(datetime.strptime(weekly, "%Y-%m-%d"))
                start_week = week_date - timedelta(days=week_date.weekday())
                end_week = start_week + timedelta(days=6)
                queryset = queryset.filter(
                    Q(start_time__date__range=[start_week.date(), end_week.date()]) |
                    Q(end_time__date__range=[start_week.date(), end_week.date()])
                )
            except ValueError:
                return Response({"error": "Invalid date format for 'weekly'. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserTrajectoryRouteSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserHeatmapAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "format": "date", "example": "2025-02-01"},
                    "end_date": {"type": "string", "format": "date", "example": "2025-02-12"},
                    "lead_ids": {"type": "array", "items": {"type": "string"}},
                    "driver_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["start_date", "end_date"]
            }
        },
        responses={200: {"type": "array", "items": {"type": "object", "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "count": {"type": "integer"}
        }}}},
    )
    def post(self, request, *args, **kwargs):
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        lead_ids = request.data.get("lead_ids", [])
        driver_ids = request.data.get("driver_ids", [])

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required."}, status=400)

        try:
            start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        user_filter = Q()
        if lead_ids:
            user_filter |= Q(guid__in=lead_ids)
        if driver_ids:
            user_filter |= Q(driver_guid__in=driver_ids)

        trajectories = (
            UserTrajectory.objects
            .filter(timestamp__range=(start_date, end_date), user__in=User.objects.filter(user_filter))
            .values("location")
            .annotate(count=Count("id"))
        )

        heatmap_data = [
            {"latitude": geo_point.y, "longitude": geo_point.x, "count": data["count"]}
            for data in trajectories if (geo_point := GEOSGeometry(data["location"]))
        ]

        return Response(heatmap_data, status=200)

