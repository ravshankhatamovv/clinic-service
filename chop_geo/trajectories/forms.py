from django import forms
from django.contrib.gis import forms as gis_forms
from .models import VehicleTrajectory


class VehicleTrajectoryForm(forms.ModelForm):
    class Meta:
        model = VehicleTrajectory
        fields = '__all__'
        widgets = {
            'location': gis_forms.OSMWidget(attrs={
                'map_width': 800,
                'map_height': 500,
                'default_lon': 69.2374775,  # Set default longitude
                'default_lat': 41.3078118,  # Set default latitude
                'default_zoom': 12,
            })
        }
