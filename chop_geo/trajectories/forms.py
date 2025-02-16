from django import forms
from django.contrib.gis import forms as gis_forms
from .models import UserTrajectory, UserTrajectoryRoute


class UserTrajectoryForm(forms.ModelForm):
    class Meta:
        model = UserTrajectory
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


class UserTrajectoryRouteForm(forms.ModelForm):
    class Meta:
        model = UserTrajectoryRoute
        fields = '__all__'
        widgets = {
            'trajectory': gis_forms.OSMWidget(attrs={
                'map_width': 800,
                'map_height': 500,
                'default_lon': 69.2374775,  # Set default longitude
                'default_lat': 41.3078118,  # Set default latitude
                'default_zoom': 12,
            }),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
