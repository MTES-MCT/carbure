from transactions.models import Site, SiteManager


class ProductionSiteManager(SiteManager):
    def get_queryset(self):
        return super().get_queryset().filter(site_type__in=Site.PRODUCTION_SITE_TYPES)


class ProductionSite(Site):
    class Meta:
        proxy = True
        verbose_name = "Site de Production"
        verbose_name_plural = "Sites de Production"

    objects = ProductionSiteManager()

    def natural_key(self):
        return {
            "address": self.address,
            "name": self.name,
            "country": self.country.natural_key(),
            "id": self.id,
            "date_mise_en_service": self.date_mise_en_service,
            "site_siret": self.site_siret,
            "postal_code": self.postal_code,
            "manager_name": self.manager_name,
            "manager_phone": self.manager_phone,
            "manager_email": self.manager_email,
            "ges_option": self.ges_option,
            "eligible_dc": self.eligible_dc,
            "dc_reference": self.dc_reference,
            "dc_number": self.dc_number,
            "city": self.city,
            "certificates": [c.natural_key() for c in self.productionsitecertificate_set.all()],
        }
