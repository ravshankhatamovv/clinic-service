from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import LineString
from django.db import models

User = get_user_model()


class UserTrajectory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trajectories')
    timestamp = models.DateTimeField()
    location = geomodels.PointField()

    class Meta:
        verbose_name = "Точки пользователей"
        verbose_name_plural = "Точки пользователей"

    def __str__(self):
        return f'{str(self.user.username)} - {self.timestamp}'


class UserTrajectoryRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    trajectory = geomodels.LineStringField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = "Линии дорог"
        verbose_name_plural = "Линии дорог"

    def __str__(self):
        return f'Route for {str(self.user.username)}'

    @staticmethod
    def generate_trajectory(user):
        """
        Генерация траектории на основе точек для указанного транспортного средства.
        """
        trajectories = UserTrajectory.objects.filter(user=user).order_by('timestamp')
        points = [(traj.location.x, traj.location.y) for traj in trajectories]

        if len(points) > 1:
            trajectory_line = LineString(points)
            return trajectory_line, trajectories.first().timestamp, trajectories.last().timestamp
        return None, None, None
