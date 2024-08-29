from django.db import models



class BluetoothCount(models.Model):
    vehicle = models.ForeignKey("trajectories.Vehicle", on_delete=models.CASCADE, related_name='bluetooth')
    timestamp = models.DateTimeField()
    count = models.IntegerField()

    def __str__(self):
        return f'{str(self.vehicle.user.name)} - {self.timestamp}'
