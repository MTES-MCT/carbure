from django.db import models

from core.models import Entity, MatierePremiere, Biocarburant, Pays


class ProductionSite(models.Model):
    GES_OPTIONS = [("Default", "Valeurs par défaut"), ("Actual", "Valeurs réelles"), ("NUTS2", "Valeurs NUTS2")]
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=False, null=False)
    country = models.ForeignKey(Pays, null=False, on_delete=models.CASCADE)
    date_mise_en_service = models.DateField(null=False, blank=False)
    ges_option = models.CharField(max_length=12, choices=GES_OPTIONS, default="Default")
    eligible_dc = models.BooleanField(default=False)
    dc_number = models.CharField(max_length=5, null=True, blank=True, default="")
    dc_reference = models.CharField(max_length=64, null=True, blank=True, default="")

    site_id = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=256, blank=True, default="")
    city = models.CharField(max_length=64, blank=True)
    postal_code = models.CharField(max_length=64, blank=True)
    gps_coordinates = models.CharField(max_length=64, blank=True, null=True, default=None)

    manager_name = models.CharField(max_length=64, blank=True)
    manager_phone = models.CharField(max_length=64, blank=True)
    manager_email = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {
            "address": self.address,
            "name": self.name,
            "country": self.country.natural_key(),
            "id": self.id,
            "date_mise_en_service": self.date_mise_en_service,
            "site_id": self.site_id,
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

    class Meta:
        db_table = "producer_sites"
        verbose_name = "Site de Production"
        verbose_name_plural = "Sites de Production"
        ordering = ["name"]


class ProductionSiteInput(models.Model):
    INPUT_STATUS = (("Pending", "En attente de validation"), ("Valid", "Validé"))

    production_site = models.ForeignKey(ProductionSite, on_delete=models.CASCADE)
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=INPUT_STATUS, default="Pending")

    def __str__(self):
        return self.matiere_premiere.name

    def natural_key(self):
        return self.matiere_premiere.natural_key()

    class Meta:
        db_table = "production_sites_input"
        verbose_name = "Site de Production - Filiere"
        verbose_name_plural = "Sites de Production - Filieres"


class ProductionSiteOutput(models.Model):
    OUTPUT_STATUS = (("Pending", "En attente de validation"), ("Valid", "Validé"))

    production_site = models.ForeignKey(ProductionSite, on_delete=models.CASCADE)
    biocarburant = models.ForeignKey(Biocarburant, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=OUTPUT_STATUS, default="Pending")

    def __str__(self):
        return self.biocarburant.name

    def natural_key(self):
        return self.biocarburant.natural_key()

    class Meta:
        db_table = "production_sites_output"
        verbose_name = "Site de Production - Biocarburant"
        verbose_name_plural = "Sites de Production - Biocarburants"
