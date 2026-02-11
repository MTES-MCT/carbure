from django.core.exceptions import ValidationError
from django.db import models

from transactions.models import Site


class ProductionSite(Site):
    class Meta:
        verbose_name = "Site de Production"
        verbose_name_plural = "Sites de Production"

    GES_OPTIONS = [("Default", "Valeurs par défaut"), ("Actual", "Valeurs réelles"), ("NUTS2", "Valeurs NUTS2")]

    date_mise_en_service = models.DateField(null=True, blank=True)
    ges_option = models.CharField(max_length=12, choices=GES_OPTIONS, default="Default")
    eligible_dc = models.BooleanField(default=False)
    dc_number = models.CharField(max_length=64, blank=True)
    dc_reference = models.CharField(max_length=64, blank=True)
    manager_name = models.CharField(max_length=64, blank=True)
    manager_phone = models.CharField(max_length=64, blank=True)
    manager_email = models.CharField(max_length=64, blank=True)

    @property
    def producer(self):
        return self.created_by

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

    def clean(self):
        if not self.date_mise_en_service:
            raise ValidationError({"date_mise_en_service": ["Ce champ est obligatoire pour les sites de production."]})
