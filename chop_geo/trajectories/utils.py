from django.contrib.auth import get_user_model

from django.contrib.gis.geos import Point
from django.utils import timezone
import random
from chop_geo.trajectories.models import Vehicle, UserTrajectoryRoute, \
    UserTrajectory

User = get_user_model()


def create_data():
    user = User.objects.first()
    vehicle, _created = Vehicle.objects.get_or_create(user=user)

    for i in range(10):
        lat = 41.0 + random.uniform(-0.01, 0.01)
        lon = 62.0 + random.uniform(-0.01, 0.01)
        timestamp = timezone.now() + timezone.timedelta(minutes=i * 5)

        UserTrajectory.objects.create(
            vehicle=vehicle,
            timestamp=timestamp,
            location=Point(lon, lat)
        )

    trajectory_line, start_time, end_time = UserTrajectoryRoute.generate_trajectory(vehicle=vehicle)

    if trajectory_line:
        UserTrajectoryRoute.objects.create(
            vehicle=vehicle,
            trajectory=trajectory_line,
            start_time=start_time,
            end_time=end_time
        )
