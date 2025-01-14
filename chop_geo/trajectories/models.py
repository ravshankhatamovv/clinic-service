import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import LineString

User = get_user_model()


class DriverCarData(models.Model):
    guid = models.UUIDField(default=uuid.uuid4,
                            primary_key=True,
                            editable=False,
                            unique=True, )

    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("Дата создания"))

    updated_at = models.DateTimeField(auto_now=True,
                                      null=True,
                                      verbose_name=_("Дата изменения"))
    car_model = models.CharField(max_length=255,
                                 verbose_name=_("Модель автомобиля"))
    car_brand = models.CharField(max_length=255,
                                 verbose_name=_("Марка машины"))
    car_service_type = models.CharField(max_length=255,
                                        verbose_name=_("Тип обслуживания автомобиля"))

    manufactured_year = models.DateField(verbose_name=_("Год выпуска"))

    government_number = models.CharField(max_length=255,
                                         verbose_name=_("Государственный номер"))
    tech_passport_number = models.CharField(max_length=255,
                                            verbose_name=_("Номер технического пароля"))
    issue_date_of_tech_passport = models.DateField(verbose_name=_("Дата выдачи технического паспорта"))

    issue_date_of_power_attorney = models.DateField(verbose_name=_("Дата выдачи доверености"))

    class Meta:
        verbose_name = _("Данные водителя об автомобиле")
        verbose_name_plural = _("Данные водителя об автомобиле")
        db_table = 'driver_car_data'
        ordering = ['created_at']

    def str(self):
        return f"{self.government_number} {self.car_model}"


class Vehicle(models.Model):
    class CHOICE_DRIVER_STATUS(models.TextChoices):
        READY_TO_WORK = 'ready_to_work', 'ready_to_work'
        HAS_WORK = 'has_work', 'has_work'
        PROCESSED = 'processed', 'processed'
        NOT_PROCESSED = 'not-processed', 'not-processed'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vehicle")
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateField(auto_now=True, null=True, verbose_name=_("Дата изменения"))
    full_name = models.CharField(max_length=255, verbose_name=_("ФИО"))
    address = models.CharField(max_length=255, verbose_name=_("Адрес"))
    phone_number = models.CharField(max_length=50, blank=True, verbose_name=_("Номер телефона"))
    card_data = models.OneToOneField(to="billing.DriverCardData", related_name='vehicle_driver_card',
                                     on_delete=models.SET_NULL,
                                     null=True, blank=True, verbose_name=_("данные карты водителя"))
    car_data = models.OneToOneField(to=DriverCarData, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.URLField(blank=True, null=True,
                            verbose_name=_("Фото профиля"))
    driver_status = models.CharField(max_length=50, blank=True, null=True,
                                     choices=CHOICE_DRIVER_STATUS,
                                     default=CHOICE_DRIVER_STATUS.READY_TO_WORK)
    last_active_time = models.DateTimeField(auto_now=True,
                                            null=True,
                                            verbose_name=_("Last active time"))

    def __str__(self):
        return str(self.user.username)


class VehicleTrajectory(models.Model):
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name='trajectories')
    timestamp = models.DateTimeField()
    location = geomodels.PointField()

    def __str__(self):
        return f'{str(self.vehicle.user.username)} - {self.timestamp}'


class VehicleTrajectoryRoute(models.Model):
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name='routes')
    trajectory = geomodels.LineStringField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'Route for {str(self.vehicle.user.username)}'

    @staticmethod
    def generate_trajectory(vehicle):
        """
        Генерация траектории на основе точек для указанного транспортного средства.
        """
        trajectories = VehicleTrajectory.objects.filter(vehicle=vehicle).order_by('timestamp')
        points = [(traj.location.x, traj.location.y) for traj in trajectories]

        if len(points) > 1:
            trajectory_line = LineString(points)
            return trajectory_line, trajectories.first().timestamp, trajectories.last().timestamp
        return None, None, None


class Model(models.Model):
    CHOICE_DRIVER_STATUS = (
        ('ready_to_work', 'ready_to_work'),
        ('has_work', 'has_work'),
        ('processed', 'processed'),
        ('not_processed', 'not_processed')
    )

    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True,
                          editable=False,
                          unique=True, )

    created_at = models.DateField(auto_now_add=True,
                                  verbose_name=_("Дата создания"))

    updated_at = models.DateField(auto_now=True,
                                  null=True,
                                  verbose_name=_("Дата изменения"))
    full_name = models.CharField(max_length=255,
                                 verbose_name=_("ФИО"))

    address = models.CharField(max_length=255,
                               verbose_name=_("Адрес"))

    phone_number = models.CharField(max_length=50,
                                    blank=True,
                                    verbose_name=_("Номер телефона"))

    first_side_passport = models.URLField(blank=True,
                                          null=True,
                                          verbose_name=_("первая сторона паспорта"))

    second_side_passport = models.URLField(blank=True,
                                           null=True,
                                           verbose_name=_("вторая сторона паспорта"))
    card_data = models.OneToOneField(to="billing.DriverCardData",
                                     related_name='driver',
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True,
                                     verbose_name=_("данные карты водителя"))

    car_data = models.OneToOneField(to=DriverCarData,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    image = models.URLField(blank=True, null=True,
                            verbose_name=_("Фото профиля"))

    driver_status = models.CharField(max_length=50,
                                     blank=True,
                                     null=True,
                                     choices=CHOICE_DRIVER_STATUS,
                                     default='ready_to_work')
    last_active_time = models.DateTimeField(auto_now=True,
                                            null=True,
                                            verbose_name=_("Last active time"))
