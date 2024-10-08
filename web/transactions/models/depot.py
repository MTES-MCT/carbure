from transactions.models import Site, SiteManager


class DepotManager(SiteManager):
    def get_queryset(self):
        return super().get_queryset().filter(site_type__in=Site.DEPOT_TYPES)


class Depot(Site):
    class Meta:
        proxy = True
        verbose_name = "Dépôt"
        verbose_name_plural = "Dépôts"
        ordering = ["name"]

    objects = DepotManager()

    def natural_key(self):
        return {
            "depot_id": self.customs_id,
            "name": self.name,
            "city": self.city,
            "country": self.country.natural_key(),
            "depot_type": self.site_type,
            "address": self.address,
            "postal_code": self.postal_code,
            "electrical_efficiency": self.electrical_efficiency,
            "thermal_efficiency": self.thermal_efficiency,
            "useful_temperature": self.useful_temperature,
        }
