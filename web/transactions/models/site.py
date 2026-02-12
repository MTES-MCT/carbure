from django.db import models


class SiteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("entitysite_set__entity")


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
    site_siret = models.CharField(max_length=64, blank=True)
    site_type = models.CharField(max_length=32, choices=SITE_TYPE, default=OTHER)
    address = models.CharField(max_length=256, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=128, blank=True)
    country = models.ForeignKey("core.Pays", null=True, blank=False, on_delete=models.SET_NULL)
    gps_coordinates = models.CharField(max_length=64, null=True, blank=True, default=None)
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

    def __str__(self):
        creator = self.created_by.name if self.created_by else ""
        return "%s - %s (%s)" % (self.name, creator, self.site_type)
