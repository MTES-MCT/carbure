from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from transactions.models import Site


class Depot(Site):
    class Meta:
        db_table = "sites_depots"
        verbose_name = "Dépôt"
        verbose_name_plural = "Dépôts"
        ordering = ["name"]

    customs_id = models.CharField(max_length=32, blank=True)
    accise = models.CharField(max_length=32, blank=True)
    electrical_efficiency = models.FloatField(
        blank=True,
        null=True,
        default=None,
        help_text="Entre 0 et 1",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    thermal_efficiency = models.FloatField(
        blank=True,
        null=True,
        default=None,
        help_text="Entre 0 et 1",
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    useful_temperature = models.FloatField(blank=True, null=True, default=None, help_text="En degrés Celsius")

    @property
    def depot_type(self):
        return self.site_type

    @property
    def depot_id(self):
        return self.customs_id

    def natural_key(self):
        return {
            "customs_id": self.customs_id,
            "name": self.name,
            "city": self.city,
            "country": self.country.natural_key(),
            "site_type": self.site_type,
            "address": self.address,
            "postal_code": self.postal_code,
            "electrical_efficiency": self.electrical_efficiency,
            "thermal_efficiency": self.thermal_efficiency,
            "useful_temperature": self.useful_temperature,
        }

    def clean(self):
        self.clear_fields()

        errors = {}

        if not self.customs_id:
            errors["customs_id"] = [_("Ce champ est obligatoire pour les dépots.")]

        if self.customs_id and Depot.objects.filter(customs_id=self.customs_id).exclude(pk=self.pk).exists():
            errors["customs_id"] = [_("Ce numéro de douane est déjà utilisé.")]

        if Site.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            errors["name"] = [_("Ce nom de dépôt est déjà utilisé.")]

        if errors:
            raise ValidationError(errors)

    def clear_fields(self):
        fields_to_clear = {
            Site.POWER_PLANT: ["thermal_efficiency", "useful_temperature"],
            Site.HEAT_PLANT: ["electrical_efficiency", "useful_temperature"],
        }

        fields = fields_to_clear.get(self.depot_type, [])
        for field in fields:
            setattr(self, field, None)
