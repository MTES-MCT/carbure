from django.db import models

from core.models import Biocarburant, MatierePremiere
from transactions.models import Site


class ProductionSiteInput(models.Model):
    INPUT_STATUS = (("Pending", "En attente de validation"), ("Valid", "Validé"))

    production_site = models.ForeignKey(Site, on_delete=models.CASCADE)
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

    production_site = models.ForeignKey(Site, on_delete=models.CASCADE)
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
