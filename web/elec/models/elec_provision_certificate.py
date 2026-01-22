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

    MANUAL = "MANUAL"
    METER_READINGS = "METER_READINGS"
    QUALICHARGE = "QUALICHARGE"
    ENR_RATIO_COMPENSATION = "ENR_RATIO_COMPENSATION"
    ADMIN_ERROR_COMPENSATION = "ADMIN_ERROR_COMPENSATION"
    SOURCES = [
        (MANUAL, MANUAL),
        (METER_READINGS, METER_READINGS),
        (QUALICHARGE, QUALICHARGE),
        (ENR_RATIO_COMPENSATION, ENR_RATIO_COMPENSATION),
        (ADMIN_ERROR_COMPENSATION, ADMIN_ERROR_COMPENSATION),
    ]

    cpo = models.ForeignKey("core.Entity", on_delete=models.CASCADE)
    quarter = models.IntegerField(choices=QUARTERS)
    year = models.IntegerField()
    operating_unit = models.CharField(max_length=64)
    source = models.CharField(max_length=32, choices=SOURCES)
    energy_amount = models.FloatField()  # unit = MWh
    remaining_energy_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
