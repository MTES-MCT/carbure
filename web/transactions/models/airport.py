from transactions.models import Site, SiteManager


class AirportManager(SiteManager):
    def get_queryset(self):
        return super().get_queryset().filter(site_type__in=Site.AIRPORT_TYPES)


class Airport(Site):
    class Meta:
        proxy = True
        verbose_name = "Aéroport"
        verbose_name_plural = "Aéroports"
        ordering = ["name"]

    objects = AirportManager()

    def natural_key(self):
        return {
            "name": self.name,
            "icao_code": self.icao_code,
            "city": self.city,
            "country": self.country.natural_key(),
            "site_type": self.site_type,
            "address": self.address,
            "postal_code": self.postal_code,
        }
