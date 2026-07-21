from django.db import models

from entity.services.geolocation import (
    ADDRESS_FIELDS,
    build_site_address,
    resolve_gps_coordinates,
    site_address_changed,
)


class SiteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("created_by", "country").prefetch_related("entitysite_set__entity")


class Site(models.Model):
    OTHER = "OTHER"
    EFS = "EFS"
    EFPE = "EFPE"
    OILDEPOT = "OIL DEPOT"
    BIOFUELDEPOT = "BIOFUEL DEPOT"
    HEAT_PLANT = "HEAT PLANT"
    POWER_PLANT = "POWER PLANT"
    COGENERATION_PLANT = "COGENERATION PLANT"
    PRODUCTION_BIOLIQUID = "PRODUCTION BIOLIQUID"
    PRODUCTION_BIOGAZ = "PRODUCTION BIOGAZ"
    EFCA = "EFCA"
    AIRPORT = "AIRPORT"

    SITE_TYPE = (
        (OTHER, "Autre"),
        (EFS, "EFS"),
        (EFPE, "EFPE"),
        (OILDEPOT, "OIL DEPOT"),
        (BIOFUELDEPOT, "BIOFUEL DEPOT"),
        (HEAT_PLANT, "HEAT PLANT"),
        (POWER_PLANT, "POWER PLANT"),
        (COGENERATION_PLANT, "COGENERATION PLANT"),
        (PRODUCTION_BIOLIQUID, "PRODUCTION BIOLIQUID"),
        (PRODUCTION_BIOGAZ, "PRODUCTION BIOGAZ"),
        (EFCA, "EFCA"),
        (AIRPORT, "AIRPORT"),
    )

    DEPOT_TYPES = [OTHER, EFS, EFPE, OILDEPOT, BIOFUELDEPOT, HEAT_PLANT, POWER_PLANT, COGENERATION_PLANT, EFCA]
    PRODUCTION_SITE_TYPES = [PRODUCTION_BIOLIQUID]
    BIOMETHANE_PRODUCTION_UNIT_TYPES = [PRODUCTION_BIOGAZ]
    AIRPORT_TYPES = [AIRPORT]

    name = models.CharField(max_length=128, blank=False)
    site_siret = models.CharField(verbose_name="SIRET", max_length=64, blank=True)
    site_type = models.CharField(max_length=32, choices=SITE_TYPE, default=OTHER)
    address = models.CharField(verbose_name="Adresse", max_length=256, blank=True)
    postal_code = models.CharField(verbose_name="Code postal", max_length=32, blank=True)
    city = models.CharField(verbose_name="Commune", max_length=128, blank=True)
    country = models.ForeignKey(
        "core.Pays",
        verbose_name="Pays",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    # longitude, latitude
    gps_coordinates = models.CharField(
        verbose_name="Coordonnées GPS",
        max_length=64,
        null=True,
        blank=True,
        default=None,
    )
    private = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.SET_NULL)

    objects = SiteManager()

    class Meta:
        db_table = "sites"
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        ordering = ["name"]

    def is_depot(self):
        return self.site_type in self.DEPOT_TYPES

    @property
    def depot_id(self):
        """Delegate to child Depot model if this site is a depot."""
        try:
            return self.depot.customs_id
        except self.__class__.depot.RelatedObjectDoesNotExist:
            return None

    @property
    def depot_type(self):
        """Return site_type if this is a depot, else None."""
        try:
            return self.depot.site_type
        except self.__class__.depot.RelatedObjectDoesNotExist:
            return None

    @property
    def producer(self):
        return self.created_by

    @property
    def dc_reference(self):
        """Delegate to child ProductionSite model."""
        try:
            return self.productionsite.dc_reference
        except self.__class__.productionsite.RelatedObjectDoesNotExist:
            return None

    def _get_previous_address_values(self):
        if self.pk is None:
            return None
        return Site.objects.filter(pk=self.pk).values(*ADDRESS_FIELDS).first()

    def _sync_gps_coordinates(self):
        address = build_site_address(self)

        # Set gps coordinates if the site is new
        if self.pk is None:
            # Set gps coordinates only if the address exists and gps_coordinates is not set
            if not self.gps_coordinates and address:
                self.gps_coordinates = resolve_gps_coordinates(address)
            return

        previous_values = self._get_previous_address_values()
        if not site_address_changed(self, previous_values):
            return

        self.gps_coordinates = resolve_gps_coordinates(address) if address else None

    def save(self, *args, **kwargs):
        self._sync_gps_coordinates()
        super().save(*args, **kwargs)

    def __str__(self):
        creator = self.created_by.name if self.created_by else ""
        return "%s - %s (%s)" % (self.name, creator, self.site_type)
