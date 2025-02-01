from django.core.exceptions import ValidationError
from django.contrib.gis.geos import LineString
from chop_geo.trajectories.models import Vehicle, VehicleTrajectory, VehicleTrajectoryRoute
from datetime import date
from celery import shared_task


@shared_task
def create_vehicle_trajectory_routes_for_today(vehicle_id):
    try:
        # Fetch the vehicle instance
        vehicle = Vehicle.objects.get(id=vehicle_id)

        # Get today's date
        today = date.today()

        # Filter trajectories for today
        daily_trajectories = VehicleTrajectory.objects.filter(
            vehicle=vehicle,
            timestamp__date=today
        ).order_by('timestamp')

        # Generate the trajectory line (LineString) and timestamps
        points = [(traj.location.x, traj.location.y) for traj in daily_trajectories]

        if len(points) > 1:
            # Create LineString for the route
            trajectory_line = LineString(points)

            # Get start and end times for today
            start_time = daily_trajectories.first().timestamp
            end_time = daily_trajectories.last().timestamp

            # Create the VehicleTrajectoryRoute instance
            route = VehicleTrajectoryRoute(
                vehicle=vehicle,
                trajectory=trajectory_line,
                start_time=start_time,
                end_time=end_time
            )
            # Save the route
            route.save()
            print(f"VehicleTrajectoryRoute created successfully for {vehicle.user.username} on {today}")
        else:
            print(f"Not enough trajectory points to create a route for {vehicle.user.username} on {today}")

    except Vehicle.DoesNotExist:
        print(f"Vehicle with ID {vehicle_id} does not exist")
    except ValidationError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

@shared_task
def create_all_vehicle_trajectory_routes_for_today():
    """
    Создает или обновляет маршруты для всех транспортных средств на основе их сегодняшних траекторий.
    """
    try:
        today = date.today()
        vehicles = Vehicle.objects.all()  # Получаем всех водителей

        for vehicle in vehicles:
            # Фильтруем траектории за сегодняшний день
            daily_trajectories = VehicleTrajectory.objects.filter(
                vehicle=vehicle,
                timestamp__date=today
            ).order_by('timestamp')

            points = [(traj.location.x, traj.location.y) for traj in daily_trajectories]

            if len(points) > 1:
                trajectory_line = LineString(points)
                start_time = daily_trajectories.first().timestamp
                end_time = daily_trajectories.last().timestamp

                # Проверяем, есть ли уже маршрут за сегодня
                route = VehicleTrajectoryRoute.objects.filter(vehicle=vehicle, start_time__date=today).first()

                if route:
                    # Обновляем существующую запись
                    route.trajectory = trajectory_line
                    route.start_time = start_time
                    route.end_time = end_time
                    route.save()
                    print(f"🔄 Route updated for {vehicle.user.username} on {today}")
                else:
                    # Создаем новый маршрут
                    route = VehicleTrajectoryRoute(
                        vehicle=vehicle,
                        trajectory=trajectory_line,
                        start_time=start_time,
                        end_time=end_time
                    )
                    route.save()
                    print(f"✅ New route created for {vehicle.user.username} on {today}")

            else:
                print(f"⚠ Not enough trajectory points for {vehicle.user.username} on {today}")

    except ValidationError as e:
        print(f"⚠ Validation error: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
