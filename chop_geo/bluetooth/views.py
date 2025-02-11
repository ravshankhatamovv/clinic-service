from datetime import datetime

from django.db.models import Sum, Q
from django.utils.timezone import make_aware
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, UserBluetoothCount


class UserBluetoothStatisticsAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={ # noqa
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
            "user_id": {"type": "string"},
            "total_count": {"type": "integer"}
        }}}},
    )
    def post(self, request, *args, **kwargs):
        start_date = request.data.get("start_date") # noqa
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

        bluetooth_counts = (
            UserBluetoothCount.objects
            .filter(timestamp__range=(start_date, end_date), user__in=User.objects.filter(user_filter))
            .values("user__id")
            .annotate(total_count=Sum("count"))
        )

        statistics_data = [
            {"user_id": data["user__id"], "total_count": data["total_count"]}
            for data in bluetooth_counts
        ]

        return Response(statistics_data, status=200)
