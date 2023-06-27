from django.db import models


class ElecProvisionCertificate(models.Model):
    class Meta:
        db_table = "elec_provision_certificate"
        verbose_name = "Certificat de Fourniture (elec)"
        verbose_name_plural = "Certificats de Fourniture (elec)"

    QUARTERS = (
        (1, "T1"),
        (2, "T2"),
        (3, "T3"),
        (4, "T4"),
    )

    entity = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.CASCADE)
    quarter = models.IntegerField(choices=QUARTERS)
    year = models.IntegerField()
    operating_unit = models.CharField(max_length=64)
    energy_amount = models.IntegerField()
    remaining_energy_amount = models.IntegerField()
