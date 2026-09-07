from django.db import models

from tiruert.models.operation import Operation
from tiruert.services.energy import avoided_emissions_tco2, energy_mj


class OperationDetailQuerySet(models.QuerySet):
    def exclude_informative(self):
        """Drop details of operations that only carry information and must not impact any computation."""
        return self.exclude(operation__type__in=Operation.BALANCE_EXCLUDED_TYPES)


class OperationDetailsManager(models.Manager.from_queryset(OperationDetailQuerySet)):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("lot", "operation", "lot__biofuel")
            .only(
                "id",
                "volume",
                "emission_rate_per_mj",
                "avoided_emissions_tco2",
                "lot__volume",
                "operation__id",
                "lot__biofuel__pci_litre",
                "lot__ghg_reduction_red_ii",
                "operation__renewable_energy_share",
            )
        )


class OperationDetail(models.Model):
    operation = models.ForeignKey("tiruert.Operation", on_delete=models.deletion.CASCADE, related_name="details")
    # Null for informative operations carrying an aggregated value instead of a per-lot breakdown
    lot = models.ForeignKey(
        "core.CarbureLot", null=True, blank=True, on_delete=models.deletion.CASCADE, related_name="tiruert_operation"
    )
    volume = models.FloatField(default=0.0)
    emission_rate_per_mj = models.FloatField(default=0.0)  # gC02/MJ réellement utilisés pour la création du lot
    avoided_emissions_tco2 = models.FloatField(null=True)  # override; formula used when null

    @property
    def energy(self):
        """Returns the energy used for lot creation in MJ, no rounded."""
        if self.lot_id is None:
            return 0

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

        if self.avoided_emissions_tco2 is not None:
            return self.avoided_emissions_tco2

        if self.lot_id is None:
            return 0

        return avoided_emissions_tco2(
            self.energy,
            self.emission_rate_per_mj,
            GHG_REFERENCE_RED_II,
        )

    class Meta:
        db_table = "tiruert_operation_details"
        verbose_name = "Détail d'opération"
        verbose_name_plural = "Détails d'opération"

    objects = OperationDetailsManager()
