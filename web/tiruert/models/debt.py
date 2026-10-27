from django.db import models
from django.db.models import F, FloatField, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from core.models import MatierePremiere

from .operation import Operation
from .operation_detail import OperationDetail


class TiruertDebtQuerySet(models.QuerySet):
    def with_remaining(self):
        """Annotate `repaid` (volume of the active DEBT_REPAYMENT operations) and `remaining` (value - repaid)."""
        repaid = (
            OperationDetail.objects.filter(
                operation__debt=OuterRef("pk"),
                operation__status__in=Operation.ACTIVE_STATUSES,
            )
            .order_by()
            .values("operation__debt")
            .annotate(total=Sum("volume"))
            .values("total")
        )
        return self.annotate(repaid=Coalesce(Subquery(repaid, output_field=FloatField()), 0.0)).annotate(
            remaining=F("value") - F("repaid")
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
