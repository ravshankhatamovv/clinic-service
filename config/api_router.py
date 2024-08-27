from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from chop_geo.trajectories.views import VehicleTrajectoryRouteViewSet
from chop_geo.users.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register('vehicle-routes', VehicleTrajectoryRouteViewSet)


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    path("trajectories/", include('chop_geo.trajectories.urls'), name='trajectories'),
]
