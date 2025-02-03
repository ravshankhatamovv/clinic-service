from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BluetoothCount(models.Model):
    vehicle = models.ForeignKey("trajectories.Vehicle", on_delete=models.CASCADE, related_name='bluetooth')
    timestamp = models.DateTimeField()
    count = models.IntegerField()

    def __str__(self):
        return f'{str(self.vehicle.user.name)} - {self.timestamp}'


class UserBluetoothCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bluetooth')
    timestamp = models.DateTimeField()
    count = models.IntegerField()

    def __str__(self):
        return f'{str(self.user.name)} - {self.timestamp}'
