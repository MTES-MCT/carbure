from django.db import models


class ElecOperationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("credited_entity", "debited_entity")
            .only(
                # Champs de l'opération
                "id",
                "type",
                "status",
                "created_at",
                "quantity",
                # Relations nécessaires
                "credited_entity_id",
                "debited_entity_id",
                # Champs des modèles liés utilisés
                "credited_entity__name",
                "debited_entity__name",
            )
        )


class ElecOperation(models.Model):
    EMISSION_RATE_PER_MJ = 183
    SECTOR = "ELEC"

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"  # Acquisition
    REJECTED = "REJECTED"  # Acquisition
    CANCELED = "CANCELED"
    DECLARED = "DECLARED"  # Teneur validation
    OPERATION_STATUSES = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (CANCELED, CANCELED),
        (DECLARED, DECLARED),
    )

    ACQUISITION_FROM_CPO = "ACQUISITION_FROM_CPO"
    ACQUISITION = "ACQUISITION"  # Only for display purposes
    CESSION = "CESSION"
    TENEUR = "TENEUR"
    OPERATION_TYPES = (
        (ACQUISITION_FROM_CPO, ACQUISITION_FROM_CPO),
        (CESSION, CESSION),
        (TENEUR, TENEUR),
    )

    type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    status = models.CharField(max_length=12, choices=OPERATION_STATUSES, default=PENDING)
    credited_entity = models.ForeignKey(
        "core.Entity", null=True, on_delete=models.deletion.CASCADE, related_name="credited_elec_operations"
    )
    debited_entity = models.ForeignKey(
        "core.Entity", null=True, on_delete=models.deletion.CASCADE, related_name="debited_elec_operations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.FloatField(default=0)  # unit = MJ

    @property
    def avoided_emissions(self):
        return ElecOperation.EMISSION_RATE_PER_MJ * self.quantity / 1e6

    objects = ElecOperationManager()

    class Meta:
        db_table = "tiruert_elec_operations"
        verbose_name = "Opération électricité"
        verbose_name_plural = "Opérations électricité"

    def is_acquisition(self, entity_id):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity_id) and self.type == ElecOperation.CESSION

    def is_credit(self, entity_id):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity_id)
