from django.db import models
from core.models import Entity

class SNCategory(models.Model):
    category_id = models.CharField(max_length=6, default='')
    description = models.CharField(max_length=512, default='')

    def natural_key(self):
        return {'category_id': self.category_id}

    def __str__(self):
        return self.category_id

    class Meta:
        db_table = 'sn_categories'
        verbose_name = 'SN Category'
        verbose_name_plural = 'SN Categories'


class SNCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField()
    download_link = models.CharField(max_length=512, default='', blank=True)

    def natural_key(self):
        scope = [s.scope.category_id for s in self.sncertificatescope_set.all()]

        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'download_link': self.download_link,
                'scope': scope,
                }

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'sn_certificates'
        verbose_name = 'SN Certificate'
        verbose_name_plural = 'SN Certificates'


class SNCertificateScope(models.Model):
    certificate = models.ForeignKey(SNCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(SNCategory, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.category_id

    class Meta:
        db_table = 'sn_certificates_scopes'
        verbose_name = 'SN Certificate Scope'
        verbose_name_plural = 'SN Certificate Scopes'

        

class EntitySNTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(SNCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "SN"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_sn_certificates'
        verbose_name = 'Certificat Système National'
        verbose_name_plural = 'Certificats Système National'
