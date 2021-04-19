from django.db import models
from core.models import Entity

class SNCertificateCategory(models.Model):
    category = models.CharField(max_length=512, default='')

    def natural_key(self):
        return {'category': self.category}

    def __str__(self):
        return self.category

    class Meta:
        db_table = 'sn_categories'
        verbose_name = 'SN Category'
        verbose_name_plural = 'SN Categories'


class SNCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    scope = models.ForeignKey(SNCertificateCategory, null=False, blank=False, on_delete=models.CASCADE)
    valid_from = models.DateField()
    valid_until = models.DateField()
    download_link = models.CharField(max_length=512, default='')

    def natural_key(self):
        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'scope': self.scope,
                'download_link': self.download_link,
                }

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'sn_certificates'
        verbose_name = 'SN Certificate'
        verbose_name_plural = 'SN Certificates'


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
