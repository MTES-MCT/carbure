from django.db import models

from elec.models.elec_charge_point import ElecChargePoint


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

    cpo = models.ForeignKey("core.Entity", on_delete=models.CASCADE)
    quarter = models.IntegerField(choices=QUARTERS)
    year = models.IntegerField()
    operating_unit = models.CharField(max_length=64)
    current_type = models.CharField(max_length=2, choices=ElecChargePoint.CURRENT_TYPES, null=True)
    energy_amount = models.FloatField()
    remaining_energy_amount = models.FloatField()
