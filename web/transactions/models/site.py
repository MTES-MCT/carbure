from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SiteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("entitysite_set__entity")


class DepotManager(SiteManager):
    def get_queryset(self):
        return super().get_queryset().filter(site_type__in=Site.DEPOT_TYPES)


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

    DEPOT_TYPES = [OTHER, EFS, EFPE, OILDEPOT, BIOFUELDEPOT, HEAT_PLANT, POWER_PLANT, COGENERATION_PLANT]

    GES_OPTIONS = [("Default", "Valeurs par défaut"), ("Actual", "Valeurs réelles"), ("NUTS2", "Valeurs NUTS2")]

    name = models.CharField(max_length=128, blank=False)
    site_siret = models.CharField(max_length=64, blank=True)
    customs_id = models.CharField(max_length=32, blank=True)
    site_type = models.CharField(max_length=32, choices=SITE_TYPE, default=OTHER)
    address = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=128, blank=True)
    country = models.ForeignKey("core.Pays", null=True, blank=False, on_delete=models.SET_NULL)
    gps_coordinates = models.CharField(max_length=64, null=True, blank=True, default=None)
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
    ges_option = models.CharField(max_length=12, choices=GES_OPTIONS, default="Default")
    eligible_dc = models.BooleanField(default=False)
    dc_number = models.CharField(max_length=64, blank=True)
    dc_reference = models.CharField(max_length=64, blank=True)
    manager_name = models.CharField(max_length=64, blank=True)
    manager_phone = models.CharField(max_length=64, blank=True)
    manager_email = models.CharField(max_length=64, blank=True)
    private = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)
    date_mise_en_service = models.DateField(null=True, blank=True)

    @property
    def producer(self):
        entity_site = self.entitysite_set.first()
        return entity_site.entity if entity_site else None

    @property
    def depot_type(self):
        return self.site_type

    @property
    def depot_id(self):
        return self.customs_id

    objects = SiteManager()
    depots = DepotManager()

    class Meta:
        db_table = "sites"
        verbose_name = "Site de stockage de carburant"
        verbose_name_plural = "Sites de stockage de carburant"
        ordering = ["name"]

    def clean(self):
        # Clear fields that are not relevant for the site type (when create depot)
        fields_to_clear = {
            "POWER PLANT": ["thermal_efficiency", "useful_temperature"],
            "HEAT PLANT": ["electrical_efficiency", "useful_temperature"],
            "COGENERATION PLANT": ["electrical_efficiency", "thermal_efficiency"],
        }

        fields = fields_to_clear.get(self.depot_type, [])
        for field in fields:
            setattr(self, field, None)

        # Check if date_mise_en_service is required for production site
        if self.site_type == self.PRODUCTION_SITE and not self.date_mise_en_service:
            raise ValidationError(
                {"date_mise_en_service": ["Ce champ est obligatoire pour les sites de type 'PRODUCTION SITE'."]}
            )

        # Check if customs_id is required for depot
        if self.site_type != self.PRODUCTION_SITE and not self.customs_id:
            raise ValidationError({"customs_id": ["Ce champ est obligatoire pour les dépots."]})

        super().clean()

    def natural_key(self):
        if self.site_type != self.PRODUCTION_SITE:
            return {
                "depot_id": self.customs_id,
                "name": self.name,
                "city": self.city,
                "country": self.country.natural_key(),
                "depot_type": self.depot_type,
                "address": self.address,
                "postal_code": self.postal_code,
                "electrical_efficiency": self.electrical_efficiency,
                "thermal_efficiency": self.thermal_efficiency,
                "useful_temperature": self.useful_temperature,
            }

    def is_depot(self):
        # Check if the site is a depot
        return self.site_type in self.DEPOT_TYPES


class ContentToUpdate(models.Model):
    model = models.CharField(max_length=64, null=False, blank=False)
    field = models.CharField(max_length=64, null=False, blank=False)
    content_id = models.IntegerField(null=False, blank=False)
    production_site = models.ForeignKey("producers.ProductionSite", null=True, on_delete=models.DO_NOTHING)
    depot = models.ForeignKey("core.Depot", null=True, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "_tmp_site_migration"
