from rest_framework import serializers
from .models import VehicleTrajectoryRoute, VehicleTrajectory
from rest_framework_gis.serializers import GeometryField


class VehicleTrajectoryRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleTrajectoryRoute
        fields = ['vehicle', 'trajectory', 'start_time', 'end_time']


class VehicleTrajectorySerializer(serializers.ModelSerializer):
    location = GeometryField()

    class Meta:
        model = VehicleTrajectory
        fields = ['timestamp', 'location']


class BulkVehicleTrajectorySerializer(serializers.ListSerializer):
    def create(self, validated_data):
        trajectories = [VehicleTrajectory(**item) for item in validated_data]
        return VehicleTrajectory.objects.bulk_create(trajectories)


class VehicleTrajectoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleTrajectory
        fields = ['timestamp', 'location']
