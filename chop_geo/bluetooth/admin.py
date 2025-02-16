from django.contrib import admin
from chop_geo.bluetooth.models import UserBluetoothCount


@admin.register(UserBluetoothCount)
class UserBluetoothCountAdmin(admin.ModelAdmin):
    ...
