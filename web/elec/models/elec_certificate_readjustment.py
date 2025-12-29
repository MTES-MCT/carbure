from django.core.validators import MinValueValidator
from django.db import models


class ElecCertificateReadjustment(models.Model):
    energy_amount = models.FloatField(validators=[MinValueValidator(0.0)])  # MWh
    created_at = models.DateField(auto_now_add=True)

    METER_READINGS = "METER_READINGS"
    QUALICHARGE = "QUALICHARGE"
    MANUAL = "MANUAL"

    error_source = models.CharField(
        max_length=16,
        choices=[
            (METER_READINGS, "Relevés"),
            (QUALICHARGE, "Qualicharge"),
            (MANUAL, "Manuel"),
        ],
    )

    reason = models.CharField(max_length=256)
