from django.db import models

from .certificate import GenericCertificate
from .entity import Entity


class EntityCertificate(models.Model):
    certificate = models.ForeignKey(GenericCertificate, blank=False, null=False, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, blank=False, null=False, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)
    checked_by_admin = models.BooleanField(default=False)
    rejected_by_admin = models.BooleanField(default=False)
    added_dt = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def all_for_entities_with_valid_national_scheme_certificate(entities):
        return EntityCertificate.objects.filter(
            entity__in=entities,
            certificate__certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            certificate__status=GenericCertificate.VALID,
        )

    def __str__(self):
        return "%s - %s" % (self.entity.name, self.certificate.certificate_id)

    class Meta:
        db_table = "carbure_entity_certificates"
        indexes = [
            models.Index(fields=["entity"]),
        ]
        verbose_name = "CarbureEntityCertificates"
        verbose_name_plural = "CarbureEntityCertificates"
