from django.db import models

from .site import Site


class Airport(Site):
    class Meta:
        db_table = "sites_airports"
        verbose_name = "Aéroport"
        verbose_name_plural = "Aéroports"
        ordering = ["name"]

    icao_code = models.CharField(max_length=32, blank=True)
    is_ue_airport = models.BooleanField(default=True)

    def natural_key(self):
        return {
            "name": self.name,
            "icao_code": self.icao_code,
            "city": self.city,
            "country": self.country.natural_key(),
            "site_type": self.site_type,
            "address": self.address,
            "postal_code": self.postal_code,
            "is_ue_airport": self.is_ue_airport,
        }
