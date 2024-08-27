from rest_framework import serializers
from .models import VehicleTrajectoryRoute, VehicleTrajectory


class VehicleTrajectoryRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleTrajectoryRoute
        fields = ['vehicle', 'trajectory', 'start_time', 'end_time']


class VehicleTrajectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleTrajectory
        fields = ['timestamp', 'location']
