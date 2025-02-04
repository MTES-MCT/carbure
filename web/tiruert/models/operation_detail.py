from django.db import models


class OperationDetail(models.Model):
    operation = models.ForeignKey("tiruert.Operation", on_delete=models.deletion.CASCADE, related_name="details")
    lot = models.ForeignKey("core.CarbureLot", on_delete=models.deletion.CASCADE, related_name="tiruert_operation")
    volume = models.FloatField(default=0.0)
    emission_rate_per_mj = models.FloatField(default=0.0)  # gC02/MJ réellement utilisés pour la création du lot

    @property
    def avoided_emissions(self):
        from tiruert.services.teneur import GHG_REFERENCE_RED_II

        lot_energy = self.lot.biofuel.pci_litre * self.volume  # (MJ) energie du lot utilisée pour la création du lot
        return (
            (GHG_REFERENCE_RED_II - self.emission_rate_per_mj) * lot_energy / 1000000
        )  # (tCO2) émissions évitées pour la création du lot

    class Meta:
        db_table = "tiruert_operation_details"
        verbose_name = "Détail d'opération"
        verbose_name_plural = "Détails d'opération"
