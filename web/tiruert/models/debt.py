from django.db import models
from django.db.models import Case, F, FloatField, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce, Greatest

from core.models import MatierePremiere
from tiruert.services.energy import (
    GHG_REFERENCE_RED_II,
    avoided_emissions_tco2_expression,
    energy_mj_expression,
)

from .operation import Operation
from .operation_detail import OperationDetail


class TiruertDebtQuerySet(models.QuerySet):
    def with_remaining(self, repayment_statuses=None):
        """Annotate remaining debt after repayments in the selected statuses (active statuses by default)."""
        if repayment_statuses is None:
            repayment_statuses = Operation.ACTIVE_STATUSES

        avoided_emissions = avoided_emissions_tco2_expression(
            energy_mj_expression(
                F("volume"),
                F("operation__renewable_energy_share"),
                F("lot__biofuel__pci_litre"),
            ),
            F("emission_rate_per_mj"),
            GHG_REFERENCE_RED_II,
        )
        repaid = (
            OperationDetail.objects.filter(
                operation__debt=OuterRef("pk"),
                operation__status__in=repayment_statuses,
            )
            .order_by()
            .values("operation__debt")
            .annotate(
                total=Sum(
                    Case(
                        When(operation__debt__type="TCO2", then=avoided_emissions),
                        default=F("volume"),
                        output_field=FloatField(),
                    )
                )
            )
            .values("total")
        )
        return self.annotate(repaid=Coalesce(Subquery(repaid, output_field=FloatField()), 0.0)).annotate(
            remaining=Case(
                When(type="TCO2", then=Greatest(F("value") - F("repaid"), Value(0.0))),
                default=F("value") - F("repaid"),
                output_field=FloatField(),
            )
        )


class TiruertDebt(models.Model):
    VOLUME = "VOLUME"
    TCO2 = "TCO2"
    DEBT_TYPES = (
        (VOLUME, VOLUME),
        (TCO2, TCO2),
    )

    lot = models.ForeignKey("core.CarbureLot", on_delete=models.CASCADE, related_name="tiruert_debts")
    type = models.CharField(max_length=10, choices=DEBT_TYPES)
    value = models.FloatField()
    entity = models.ForeignKey("core.Entity", on_delete=models.CASCADE, related_name="tiruert_debts")
    biofuel = models.ForeignKey("core.Biocarburant", on_delete=models.PROTECT)
    customs_category = models.CharField(max_length=20, choices=MatierePremiere.MP_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager.from_queryset(TiruertDebtQuerySet)()

    class Meta:
        db_table = "tiruert_debts"
        verbose_name = "Dette"
        verbose_name_plural = "Dettes"
        indexes = [models.Index(fields=["entity", "biofuel", "customs_category"], name="tiruert_debt_entity_idx")]
