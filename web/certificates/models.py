from django.db import models
from core.models import Biocarburant, Entity, EntityCertificate, MatierePremiere, Pays
from producers.models import ProductionSite

class ProductionSiteCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(ProductionSite, null=True, on_delete=models.CASCADE)
    certificate = models.ForeignKey(EntityCertificate, null=True, blank=True, on_delete=models.CASCADE)
    
    def natural_key(self):
        return {'type': self.certificate.certificate.certificate_type, 'certificate_id': self.certificate.certificate.certificate_id}

    class Meta:
        db_table = 'production_sites_certificates'
        verbose_name = 'Certificat de site de production'
        verbose_name_plural = 'Certificats de sites de productions'


class DoubleCountingRegistration(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    registered_address = models.TextField(blank=False, null=False)
    valid_from = models.DateField(blank=False, null=False)
    valid_until = models.DateField(blank=False, null=False)

    def natural_key(self):
        return {'certificate_id': self.certificate_id, 'certificate_holder': self.certificate_holder, 'registered_address': self.registered_address, 'valid_from': self.valid_from, 'valid_until': self.valid_until}

    class Meta:
        db_table = 'double_counting_registrations'
        verbose_name = 'Certificat Double Compte'
        verbose_name_plural = 'Certificats Double Compte'    


class DoubleCountingRegistrationInputOutput(models.Model):
    certificate = models.ForeignKey(DoubleCountingRegistration, blank=False, null=False, on_delete=models.CASCADE)
    biofuel = models.ForeignKey(Biocarburant, null=False, blank=False, on_delete=models.CASCADE)
    feedstock = models.ForeignKey(MatierePremiere, blank=True, null=True, on_delete=models.CASCADE)

    def natural_key(self):
        return {'biofuel': self.biofuel.natural_key(), 'feedstock': self.feedstock.natural_key() if self.feedstock else ''}

    class Meta:
        db_table = 'double_counting_registrations_scope'
        verbose_name = 'Périmètre Certificat Double Compte'
        verbose_name_plural = 'Périmètres Certificats Double Compte'
