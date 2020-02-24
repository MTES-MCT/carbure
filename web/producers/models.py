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
