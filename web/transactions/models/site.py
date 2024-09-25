from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import Pays
from producers.models import Depot, ProductionSite


class Site(models.Model):
    OTHER = "OTHER"
    EFS = "EFS"
    EFPE = "EFPE"
    OILDEPOT = "OIL DEPOT"
    BIOFUELDEPOT = "BIOFUEL DEPOT"
    HEAT_PLANT = "HEAT PLANT"
    POWER_PLANT = "POWER PLANT"
    COGENERATION_PLANT = "COGENERATION PLANT"
    PRODUCTION_SITE = "PRODUCTION SITE"

    SITE_TYPE = (
        (OTHER, "Autre"),
        (EFS, "EFS"),
        (EFPE, "EFPE"),
        (OILDEPOT, "OIL DEPOT"),
        (BIOFUELDEPOT, "BIOFUEL DEPOT"),
        (HEAT_PLANT, "HEAT PLANT"),
        (POWER_PLANT, "POWER PLANT"),
        (COGENERATION_PLANT, "COGENERATION PLANT"),
        (PRODUCTION_SITE, "PRODUCTION SITE"),
    )

    GES_OPTIONS = [("Default", "Valeurs par défaut"), ("Actual", "Valeurs réelles"), ("NUTS2", "Valeurs NUTS2")]

    name = models.CharField(max_length=128, null=False, blank=False)
    site_id = models.CharField(max_length=64, blank=True)
    customs_id = models.CharField(max_length=32, null=False, blank=False)
    site_type = models.CharField(max_length=32, choices=SITE_TYPE, default=OTHER)
    address = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    country = models.ForeignKey(Pays, null=True, blank=False, on_delete=models.SET_NULL)
    gps_coordinates = models.CharField(max_length=64, blank=True, null=True, default=None)
    accise = models.CharField(max_length=32, blank=True, null=True, default=None)
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
    ges_option = models.CharField(max_length=12, choices=GES_OPTIONS, default="Default")
    eligible_dc = models.BooleanField(default=False)
    dc_number = models.CharField(max_length=64, null=True, blank=True, default="")
    dc_reference = models.CharField(max_length=64, null=True, blank=True, default="")
    manager_name = models.CharField(max_length=64, blank=True)
    manager_phone = models.CharField(max_length=64, blank=True)
    manager_email = models.CharField(max_length=64, blank=True)
    private = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = "sites"
        verbose_name = "Site de stockage de carburant"
        verbose_name_plural = "Sites de stockage de carburant"
        ordering = ["name"]

    def clean(self):
        fields_to_clear = {
            "POWER PLANT": ["thermal_efficiency", "useful_temperature"],
            "HEAT PLANT": ["electrical_efficiency", "useful_temperature"],
            "COGENERATION PLANT": ["electrical_efficiency", "thermal_efficiency"],
        }

        fields = fields_to_clear.get(self.depot_type, [])
        for field in fields:
            setattr(self, field, None)

        super().clean()


class ContentToUpdate(models.Model):
    model = models.CharField(max_length=64, null=False, blank=False)
    content_id = models.IntegerField(null=False, blank=False)
    production_site = models.ForeignKey(ProductionSite, on_delete=models.DO_NOTHING)
    depot = models.ForeignKey(Depot, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "_tmp_site_migration"
