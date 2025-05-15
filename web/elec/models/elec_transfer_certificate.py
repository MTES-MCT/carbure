from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    supplier = models.ForeignKey(
        "core.Entity", null=True, blank=True, on_delete=models.CASCADE, related_name="sent_transfer_certificates"
    )
    client = models.ForeignKey(
        "core.Entity", null=True, blank=True, on_delete=models.CASCADE, related_name="received_transfer_certificates"
    )
    transfer_date = models.DateField()
    accepted_date = models.DateField(null=True, blank=True)
    energy_amount = models.FloatField()  # unit = MWh
    comment = models.CharField(max_length=256, null=True, blank=True)

    used_in_tiruert = models.BooleanField(default=False)
    consumption_date = models.DateField(null=True, blank=True)

    def generate_certificate_id(self):
        self.certificate_id = f"E{self.transfer_date.year}{self.transfer_date.month}-FR-{self.id}"


# Automatically create certificate id
@receiver(post_save, sender=ElecTransferCertificate)
def lot_post_save_gen_certificate_id(sender, instance, created, update_fields=None, *args, **kwargs):
    if update_fields is None:
        update_fields = {}
    old_certificate_id = instance.certificate_id
    instance.generate_certificate_id()

    if instance.certificate_id != old_certificate_id:
        instance.save(update_fields=["certificate_id"])
