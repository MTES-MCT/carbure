from django.db import models


class ElecTransferCertificate(models.Model):
    class Meta:
        db_table = "elec_transfer_certificate"
        verbose_name = "Certificat de Cession (elec)"
        verbose_name_plural = "Certificats de Cession (elec)"

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    STATUS = [(PENDING, PENDING), (ACCEPTED, ACCEPTED), (REJECTED, REJECTED)]

    certificate_id = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=STATUS, default=PENDING)
    supplier = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.CASCADE, related_name="sent_transfer_certificates")  # fmt:skip
    client = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.CASCADE, related_name="received_transfer_certificates")  # fmt:skip
    transfer_date = models.DateField()
    energy_amount = models.IntegerField()
