from django.db import models


class OperationDetail(models.Model):
    operation = models.ForeignKey("tiruert.Operation", on_delete=models.deletion.CASCADE, related_name="details")
    lot = models.ForeignKey("core.CarbureLot", on_delete=models.deletion.CASCADE, related_name="tiruert_operation")
    volume = models.FloatField(default=0.0)
    saved_ghg = models.FloatField(default=0.0)

    class Meta:
        db_table = "tiruert_operation_details"
        verbose_name = "Détail d'opération"
        verbose_name_plural = "Détails d'opération"
