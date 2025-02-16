from datetime import date

from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString
from django.core.exceptions import ValidationError

from chop_geo.trajectories.models import UserTrajectory, UserTrajectoryRoute

User = get_user_model()


@shared_task
def create_all_vehicle_trajectory_routes_for_today():
    """
    Создает или обновляет маршруты для всех транспортных средств на основе их сегодняшних траекторий.
    """
    try:
        today = date.today()
        users = User.objects.all()  # Получаем всех водителей

        for user in users:
            # Фильтруем траектории за сегодняшний день
            daily_trajectories = UserTrajectory.objects.filter(
                user=user,
                timestamp__date=today
            ).order_by('timestamp')

            points = [(traj.location.x, traj.location.y) for traj in daily_trajectories]

            if len(points) > 1:
                trajectory_line = LineString(points)
                start_time = daily_trajectories.first().timestamp
                end_time = daily_trajectories.last().timestamp

                # Проверяем, есть ли уже маршрут за сегодня
                route = UserTrajectoryRoute.objects.filter(user=user, start_time__date=today).first()

                if route:
                    # Обновляем существующую запись
                    route.trajectory = trajectory_line
                    route.start_time = start_time
                    route.end_time = end_time
                    route.save()
                    print(f"🔄 Route updated for {user.username} on {today}")
                else:
                    # Создаем новый маршрут
                    route = UserTrajectoryRoute(
                        user=user,
                        trajectory=trajectory_line,
                        start_time=start_time,
                        end_time=end_time
                    )
                    route.save()
                    print(f"✅ New route created for {user.username} on {today}")

            else:
                print(f"⚠ Not enough trajectory points for {user.username} on {today}")

    except ValidationError as e:
        print(f"⚠ Validation error: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
