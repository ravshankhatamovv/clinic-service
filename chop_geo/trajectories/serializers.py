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
        trajectories_data = validated_data['trajectories']
        trajectories = [VehicleTrajectory(**item) for item in trajectories_data]
        return VehicleTrajectory.objects.bulk_create(trajectories)


class VehicleTrajectoryCreateSerializer(serializers.Serializer):
    data = VehicleTrajectorySerializer(many=True, write_only=True)

    def create(self, validated_data):
        trajectories_list = validated_data['data']
        vehicle = validated_data['vehicle']

        trajectories = [VehicleTrajectory(**item, vehicle=vehicle) for item in trajectories_list]
        VehicleTrajectory.objects.bulk_create(trajectories)
        return {"status": "ok"}
