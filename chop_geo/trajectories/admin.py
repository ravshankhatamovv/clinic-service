from django.contrib import admin
from .models import UserTrajectory, UserTrajectoryRoute
from .forms import UserTrajectoryForm, UserTrajectoryRouteForm


@admin.register(UserTrajectoryRoute)
class VehicleTrajectoryRouteAdmin(admin.ModelAdmin):
    form = UserTrajectoryRouteForm
    list_display = ["__str__", "start_time", "end_time"]


@admin.register(UserTrajectory)
class VehicleTrajectoryAdmin(admin.ModelAdmin):
    form = UserTrajectoryForm
