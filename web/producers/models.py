from django.db import models

from core.models import Entity, MatierePremiere, Biocarburant, Pays


class ProductionSite(models.Model):
    GES_OPTIONS = [('Default', 'Valeurs par défaut'), ('Actual', 'Valeurs réelles')]
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=False, null=False)
    country = models.ForeignKey(Pays, null=False, on_delete=models.CASCADE)
    date_mise_en_service = models.DateField(null=False, blank=False)
    ges_option = models.CharField(max_length=12, choices=GES_OPTIONS, default='Default')
    eligible_dc = models.BooleanField(default=False)
    dc_reference = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'name': self.name, 'country': self.country.natural_key(), 'id': self.id}

    class Meta:
        db_table = 'producer_sites'
        verbose_name = 'Site de Production'
        verbose_name_plural = 'Sites de Production'


class ProductionSiteInput(models.Model):
    INPUT_STATUS = (('Pending', 'En attente de validation'), ('Valid', 'Validé'))

    production_site = models.ForeignKey(ProductionSite, on_delete=models.CASCADE)
    matiere_premiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=INPUT_STATUS, default="Pending")

    def __str__(self):
        return self.matiere_premiere.name

    class Meta:
        db_table = 'production_sites_input'
        verbose_name = 'Site de Production - Filiere'
        verbose_name_plural = 'Sites de Production - Filieres'


class ProductionSiteOutput(models.Model):
    OUTPUT_STATUS = (('Pending', 'En attente de validation'), ('Valid', 'Validé'))

    production_site = models.ForeignKey(ProductionSite, on_delete=models.CASCADE)
    biocarburant = models.ForeignKey(Biocarburant, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=OUTPUT_STATUS, default="Pending")

    def __str__(self):
        return self.biocarburant.name

    class Meta:
        db_table = 'production_sites_output'
        verbose_name = 'Site de Production - Biocarburant'
        verbose_name_plural = 'Sites de Production - Biocarburants'


class ProducerCertificate(models.Model):
    CERTIF_STATUS_CHOICES = [("Pending", "En Attente de validation"), ("Valid", "Validé"), ("Expired", "Expiré")]
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(ProductionSite, null=True, on_delete=models.CASCADE)
    expiration = models.DateField()
    date_added = models.DateField(auto_now_add=True)
    certificate = models.FileField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=CERTIF_STATUS_CHOICES, default="Pending")
    certificate_id = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'producer_certificates'
        verbose_name = 'Certificat'
        verbose_name_plural = 'Certificats'


