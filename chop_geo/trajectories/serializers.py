from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField

from chop_geo.bluetooth.models import UserBluetoothCount
from .models import UserTrajectory, UserTrajectoryRoute


class UserTrajectorySerializer(serializers.ModelSerializer):
    location = GeometryField()
    bluetooth = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserTrajectory
        fields = ['timestamp', 'location', 'bluetooth']


class VehicleTrajectoryCreateSerializer(serializers.Serializer):
    data = UserTrajectorySerializer(many=True, write_only=True)

    def create(self, validated_data):
        trajectories_list = validated_data['data']
        user = validated_data['user']

        trajectories = []
        bluetooths = []
        for trajectory in trajectories_list:
            bluetooth_count = trajectory.pop("bluetooth", None)
            if bluetooth_count > 0:
                bluetooths.append(
                    UserBluetoothCount(user=user,
                                       count=bluetooth_count,
                                       timestamp=trajectory["timestamp"])
                )
            trajectories.append(UserTrajectory(**trajectory, user=user))

        UserTrajectory.objects.bulk_create(trajectories)
        UserBluetoothCount.objects.bulk_create(bluetooths)
        return {"status": "ok"}


class UserTrajectoryRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrajectoryRoute
        fields = '__all__'
