from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from transactions.models import Site, SiteManager


class DepotManager(SiteManager):
    def get_queryset(self):
        return super().get_queryset().filter(site_type__in=Site.DEPOT_TYPES)


class Depot(Site):
    class Meta:
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

    objects = DepotManager()

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
        # Clear fields that are not relevant for the site type (when create depot)
        self.clear_fields()

        # Check if customs_id is required for depot
        if not self.customs_id:
            raise ValidationError({"customs_id": ["Ce champ est obligatoire pour les dépots."]})

        site = (
            Site.objects.filter(models.Q(customs_id=self.customs_id) | models.Q(name=self.name)).exclude(id=self.id).first()
        )

        if site:
            errors = {}
            if site.customs_id == self.customs_id:
                errors["customs_id"] = [_("Ce numéro de douane est déjà utilisé.")]
            if site.name == self.name:
                errors["site_name"] = [_("Ce nom de dépôt est déjà utilisé.")]

            raise ValidationError(errors)

    def clear_fields(self):
        fields_to_clear = {
            Site.POWER_PLANT: ["thermal_efficiency", "useful_temperature"],
            Site.HEAT_PLANT: ["electrical_efficiency", "useful_temperature"],
        }

        fields = fields_to_clear.get(self.depot_type, [])
        for field in fields:
            setattr(self, field, None)
