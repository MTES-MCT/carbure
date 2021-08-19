from django.db import models
from django.contrib.auth import get_user_model

from core.models import Entity, MatierePremiere, Pays, Biocarburant
from producers.models import ProductionSite

usermodel = get_user_model()

class DoubleCountingAgreement(models.Model):
    PENDING = 'PENDING'
    REJECTED = 'REJECTED'
    ACCEPTED = 'ACCEPTED'
    LAPSED = 'LAPSED'

    DCA_STATUS_CHOICES = ((PENDING, PENDING), (REJECTED, REJECTED), (ACCEPTED, ACCEPTED), (LAPSED, LAPSED))
    
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(ProductionSite, on_delete=models.CASCADE)
    period_start = models.DateField(null=False, blank=False)
    period_end = models.DateField(null=False, blank=False)
    status = models.CharField(max_length=32, choices=DCA_STATUS_CHOICES, default=PENDING)

    dgec_validated = models.BooleanField(default=False)
    dgec_validator = models.ForeignKey(usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name='dgec_validator')
    dgec_validated_dt = models.DateTimeField(null=True, blank=True)

    dgddi_validated = models.BooleanField(default=False)
    dgddi_validator = models.ForeignKey(usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name='dgddi_validator')
    dgddi_validated_dt = models.DateTimeField(null=True, blank=True)

    dgpe_validated = models.BooleanField(default=False)
    dgpe_validator = models.ForeignKey(usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name='dgpe_validator')
    dgpe_validated_dt = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'double_counting_agreements'
        verbose_name = 'Dossier Double Compte'
        verbose_name_plural = 'Dossiers Double Compte'


class DoubleCountingSourcing(models.Model):
    dca = models.ForeignKey(DoubleCountingAgreement, on_delete=models.CASCADE)
    year = models.IntegerField(blank=False, null=False)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    origin_country = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name='origin_country')
    supply_country = models.ForeignKey(Pays, blank=True, null=True, on_delete=models.CASCADE, related_name='supply_country')
    transit_country = models.ForeignKey(Pays, blank=True, null=True, on_delete=models.CASCADE, related_name='transit_country')
    metric_tonnes = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = 'double_counting_sourcing'
        verbose_name = 'Sourcing Double Compte'
        verbose_name_plural = 'Sourcing Double Compte'


class DoubleCountingProduction(models.Model):
    dca = models.ForeignKey(DoubleCountingAgreement, on_delete=models.CASCADE)
    year = models.IntegerField(blank=False, null=False)
    biofuel = models.ForeignKey(Biocarburant, on_delete=models.CASCADE)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)    
    metric_tonnes = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = 'double_counting_production'
        verbose_name = 'Production Double Compte'
        verbose_name_plural = 'Production Double Compte'

