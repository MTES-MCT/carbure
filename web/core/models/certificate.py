from typing import Tuple

from django.db import models
from django.utils import timezone

from .entity import Entity


class GenericCertificate(models.Model):
    SYSTEME_NATIONAL = "SYSTEME_NATIONAL"
    ISCC = "ISCC"
    REDCERT = "REDCERT"
    DBS = "2BS"
    KZR_INIG = "KZR_INIG"
    CERTIFICATE_TYPES = (
        (SYSTEME_NATIONAL, SYSTEME_NATIONAL),
        (ISCC, ISCC),
        (REDCERT, REDCERT),
        (DBS, DBS),
        (KZR_INIG, KZR_INIG),
    )

    certificate_id = models.CharField(max_length=64, blank=False, null=False)
    certificate_type = models.CharField(max_length=32, null=False, blank=False, choices=CERTIFICATE_TYPES)
    certificate_holder = models.CharField(max_length=512, null=False, blank=False)
    certificate_issuer = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)
    valid_from = models.DateField(null=False, blank=False)
    valid_until = models.DateField(null=False, blank=False)
    download_link = models.CharField(max_length=512, default=None, null=True)
    scope = models.JSONField(null=True)  # TODO turn into CharField
    input = models.JSONField(null=True)  # TODO check if we need this
    output = models.JSONField(null=True)

    PENDING = "PENDING"  # certificat pas encore valide
    VALID = "VALID"  # certificat valide
    SUSPENDED = "SUSPENDED"  # certificat temporairement invalidé
    WITHDRAWN = "WITHDRAWN"  # certificat annulé de façon permanente par le schéma volontaire
    TERMINATED = "TERMINATED"  # certificat volontairement arrêté par l'opérateur économique
    EXPIRED = "EXPIRED"  # certificat arrivé à échéance

    status = models.CharField(
        max_length=16,
        choices=[
            (PENDING, "En attente"),
            (VALID, "Valide"),
            (SUSPENDED, "Suspendu"),
            (WITHDRAWN, "Retiré"),
            (TERMINATED, "Interrompu"),
            (EXPIRED, "Expiré"),
        ],
    )

    last_status_update = models.DateField()

    @staticmethod
    def bulk_create_or_update(certificates: list[dict], status: str) -> Tuple[list, list]:
        from core.utils import bulk_update_or_create  # this is imported here to avoid circular dependencies

        current_date = timezone.localdate()

        # udpate the `last_status_update` field only for certificates that actually changed status
        existing_certs = GenericCertificate.objects.filter(certificate_id__in=[x["certificate_id"] for x in certificates])
        existing_certs.exclude(status=status).update(last_status_update=current_date)

        return bulk_update_or_create(
            GenericCertificate,
            "certificate_id",
            certificates,
            defaults={"last_status_update": current_date},  # only set the `last_status_update` column on new rows
        )

    class Meta:
        db_table = "carbure_certificates"
        indexes = [
            models.Index(fields=["certificate_type"]),
        ]
        verbose_name = "CarbureCertificates"
        verbose_name_plural = "CarbureCertificates"


class EntityCertificate(models.Model):
    certificate = models.ForeignKey(GenericCertificate, blank=False, null=False, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, blank=False, null=False, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)
    checked_by_admin = models.BooleanField(default=False)
    rejected_by_admin = models.BooleanField(default=False)
    added_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.entity.name, self.certificate.certificate_id)

    class Meta:
        db_table = "carbure_entity_certificates"
        indexes = [
            models.Index(fields=["entity"]),
        ]
        verbose_name = "CarbureEntityCertificates"
        verbose_name_plural = "CarbureEntityCertificates"
