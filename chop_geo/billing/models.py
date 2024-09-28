import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class DriverCardData(models.Model):
    guid = models.UUIDField(default=uuid.uuid4,
                            editable=False,
                            unique=True)

    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("Дата создания"))

    updated_at = models.DateTimeField(auto_now=True,
                                      null=True,
                                      verbose_name=_("Дата изменения"))
    card_number = models.CharField(max_length=16,
                                   null=True,
                                   blank=True,
                                   verbose_name=_("Номер карты"))

    class Meta:
        verbose_name = _("Данные карты водителя")
        verbose_name_plural = _("Данные карты водителя")
        db_table = 'driver_card_data'
        ordering = ['created_at']

    def str(self):
        return self.card_number
