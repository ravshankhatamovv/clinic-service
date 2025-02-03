from django.contrib import admin
from .models import Vehicle, UserTrajectory, UserTrajectoryRoute
from .forms import UserTrajectoryForm, UserTrajectoryRouteForm


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    ...


@admin.register(UserTrajectoryRoute)
class VehicleTrajectoryRouteAdmin(admin.ModelAdmin):
    form = UserTrajectoryRouteForm
    list_display = ["__str__", "start_time", "end_time"]


@admin.register(UserTrajectory)
class VehicleTrajectoryAdmin(admin.ModelAdmin):
    form = UserTrajectoryForm
