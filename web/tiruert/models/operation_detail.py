from django.db import models

from tiruert.services.energy import avoided_emissions_tco2, effective_emission_rate_per_mj, energy_mj


class OperationDetailsManager(models.Manager):
    def get_effective_emission_rates_by_lot(self, lot_ids):
        details = (
            self.filter(lot_id__in=lot_ids)
            .exclude(models.Q(operation__type="CORRECTION", volume=0, emission_rate_per_mj_delta__isnull=False))
            .order_by("lot_id", "operation__created_at", "id")
            .values_list("lot_id", "emission_rate_per_mj", "emission_rate_per_mj_delta")
        )
        rates = {}
        for lot_id, reference, delta in details:
            if lot_id not in rates:
                rates[lot_id] = effective_emission_rate_per_mj(reference, delta)
        return rates

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("lot", "operation", "lot__biofuel")
            .only(
                "id",
                "volume",
                "emission_rate_per_mj",
                "emission_rate_per_mj_delta",
                "lot__volume",
                "operation__id",
                "lot__biofuel__pci_litre",
                "lot__ghg_reduction_red_ii",
                "operation__renewable_energy_share",
            )
        )


class OperationDetail(models.Model):
    operation = models.ForeignKey("tiruert.Operation", on_delete=models.deletion.CASCADE, related_name="details")
    lot = models.ForeignKey("core.CarbureLot", on_delete=models.deletion.CASCADE, related_name="tiruert_operation")
    volume = models.FloatField(default=0.0)
    emission_rate_per_mj = models.FloatField(default=0.0)  # gC02/MJ réellement utilisés pour la création du lot
    emission_rate_per_mj_delta = models.FloatField(null=True, blank=True, default=None)

    @property
    def effective_emission_rate_per_mj(self):
        return effective_emission_rate_per_mj(self.emission_rate_per_mj, self.emission_rate_per_mj_delta)

    @property
    def energy(self):
        """Returns the energy used for lot creation in MJ, no rounded."""
        renewable_energy_share = getattr(self.operation, "renewable_energy_share", 1)
        return energy_mj(
            self.volume,
            self.lot.biofuel.pci_litre,
            renewable_energy_share,
        )

    @property
    def avoided_emissions(self):
        """Return the saved emissions in tCO2, no rounded."""
        from tiruert.services.teneur import GHG_REFERENCE_RED_II

        return avoided_emissions_tco2(
            self.energy,
            self.emission_rate_per_mj,
            GHG_REFERENCE_RED_II,
        )

    @property
    def corrected_avoided_emissions(self):
        from tiruert.services.teneur import GHG_REFERENCE_RED_II

        return avoided_emissions_tco2(
            self.energy,
            self.effective_emission_rate_per_mj,
            GHG_REFERENCE_RED_II,
        )

    class Meta:
        db_table = "tiruert_operation_details"
        verbose_name = "Détail d'opération"
        verbose_name_plural = "Détails d'opération"

    objects = OperationDetailsManager()
