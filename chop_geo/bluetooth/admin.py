from django.contrib import admin
from chop_geo.bluetooth.models import BluetoothCount


@admin.register(BluetoothCount)
class BluetoothCountAdmin(admin.ModelAdmin):
    ...
