from django.db import models

from core.models import Entity

class AttestationProducer(models.Model):
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE)
    period = models.CharField(max_length=7, blank=False, null=False)
    deadline = models.DateField(blank=False, null=False)

    def __str__(self):
        return '%s - %s' % (self.period, self.producer.name)

    class Meta:
        db_table = 'producer_attestations'
        verbose_name = 'Attestation de Durabilité'
        verbose_name_plural = 'Attestations de Durabilité'	

class ProductionSite(models.Model):
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=False, null=False)
    identifiant = models.CharField(max_length=64, blank=False, null=False)
    num_accise = models.CharField(max_length=64, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'producer_sites'
        verbose_name = 'Site de Production'
        verbose_name_plural = 'Sites de Production'	
