from rest_framework import serializers
from .models import VehicleTrajectoryRoute, VehicleTrajectory
from chop_geo.bluetooth.models import BluetoothCount
from rest_framework_gis.serializers import GeometryField


class VehicleTrajectoryRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleTrajectoryRoute
        fields = ['vehicle', 'trajectory', 'start_time', 'end_time']


class VehicleTrajectorySerializer(serializers.ModelSerializer):
    location = GeometryField()
    bluetooth = serializers.IntegerField(write_only=True)

    class Meta:
        model = VehicleTrajectory
        fields = ['timestamp', 'location']


class VehicleTrajectoryCreateSerializer(serializers.Serializer):
    data = VehicleTrajectorySerializer(many=True, write_only=True)

    def create(self, validated_data):
        trajectories_list = validated_data['data']
        vehicle = validated_data['vehicle']

        trajectories = []
        bluetooths = []
        for trajectory in trajectories_list:
            bluetooth_count = trajectory.pop("bluetooth", None)
            if bluetooth_count:
                bluetooths.append(
                    BluetoothCount(vehicle=vehicle,
                                   count=bluetooth_count,
                                   timestamp=trajectory["timestamp"])
                )
            trajectories.append(VehicleTrajectory(**trajectory, vehicle=vehicle))

        VehicleTrajectory.objects.bulk_create(trajectories)
        BluetoothCount.objects.bulk_create(bluetooths)
        return {"status": "ok"}
