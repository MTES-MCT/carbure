from django.db import models
from math import floor


class ElecProvisionCertificate(models.Model):
    class Meta:
        db_table = "elec_provision_certificate"
        verbose_name = "Certificat de Fourniture (elec)"
        verbose_name_plural = "Certificats de Fourniture (elec)"

    entity = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.CASCADE)
    quarter = models.CharField(max_length=64)
    oeprating_unit = models.CharField(max_length=64)
    energy_amount = models.IntegerField()
    remaining_energy_amount = models.IntegerField()
