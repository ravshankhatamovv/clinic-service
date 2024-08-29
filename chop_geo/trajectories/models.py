from django.contrib.auth import get_user_model
from django.db import models

from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import LineString

User = get_user_model()


class Vehicle(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vehicle")

    def __str__(self):
        return str(self.user.name)


class VehicleTrajectory(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trajectories')
    timestamp = models.DateTimeField()
    location = geomodels.PointField()

    def __str__(self):
        return f'{str(self.vehicle.user.name)} - {self.timestamp}'


class VehicleTrajectoryRoute(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes')
    trajectory = geomodels.LineStringField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'Route for {str(self.vehicle.user.name)} from {self.start_time} to {self.end_time}'

    @staticmethod
    def generate_trajectory(vehicle):
        """
        Генерация траектории на основе точек для указанного транспортного средства.
        """
        trajectories = VehicleTrajectory.objects.filter(vehicle=vehicle).order_by('timestamp')
        points = [(traj.location.x, traj.location.y) for traj in trajectories]

        if len(points) > 1:
            trajectory_line = LineString(points)
            return trajectory_line, trajectories.first().timestamp, trajectories.last().timestamp
        return None, None, None
