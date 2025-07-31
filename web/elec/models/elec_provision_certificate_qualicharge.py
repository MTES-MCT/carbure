from django.db import models


class ElecProvisionCertificateQualicharge(models.Model):
    DGEC = "DGEC"
    CPO = "CPO"
    BOTH = "BOTH"
    NO_ONE = "NO_ONE"
    VALIDATION_CHOICES = (
        (NO_ONE, NO_ONE),
        (DGEC, DGEC),
        (CPO, CPO),
        (BOTH, BOTH),
    )

    cpo = models.ForeignKey("core.Entity", on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    year = models.IntegerField()
    operating_unit = models.CharField(max_length=64)
    station_id = models.CharField(max_length=64)
    energy_amount = models.FloatField()  # unit = MWh
    is_controlled_by_qualicharge = models.BooleanField(default=False)
    validated_by = models.CharField(max_length=16, choices=VALIDATION_CHOICES, default=NO_ONE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "elec_provision_certificate_qualicharge"
        verbose_name = "Certificat de Fourniture intermédiaire (elec)"
        verbose_name_plural = "Certificats de Fourniture intermédiaires (elec)"

    def __str__(self):
        return f"{self.cpo.name} - {self.station_id} - {self.date_from} to {self.date_to}"
