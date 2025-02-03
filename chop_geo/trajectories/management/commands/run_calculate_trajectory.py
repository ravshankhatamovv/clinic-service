from django.core.management.base import BaseCommand
from chop_geo.trajectories.tasks import create_all_vehicle_trajectory_routes_for_today


class Command(BaseCommand):
    help = "Trigger a Celery task with a delay"

    def handle(self, *args, **kwargs):
        self.stdout.write("Scheduling task...")

        task = create_all_vehicle_trajectory_routes_for_today.apply_async(countdown=1)

        self.stdout.write(f"Task scheduled with ID: {task.id}")
