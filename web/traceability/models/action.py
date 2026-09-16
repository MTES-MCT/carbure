from decimal import Decimal

from django.db import models, transaction
from django.db.models import CharField, OuterRef, Q, QuerySet, Subquery, Value
from django.db.models.functions import Concat, ExtractMonth, ExtractYear, LPad
from django.utils.translation import gettext_lazy as _

from traceability.services.quantities import quantities_db_annotation

from .action_status import ActionStatus


class ActionManager(models.Manager):
    def get_queryset(self):
        first_status_subquery = ActionStatus.objects.filter(action=OuterRef("id")).order_by("created_at", "id")
        latest_status_subquery = ActionStatus.objects.filter(action=OuterRef("id")).order_by("-created_at", "-id")

        return (
            super()
            .get_queryset()
            .select_related("holder", "material", "site", "parent", "certificate")
            .annotate(status=Subquery(latest_status_subquery.values("status")[:1]))
            .annotate(created_at=Subquery(first_status_subquery.values("created_at")[:1]))
            .annotate(updated_at=Subquery(latest_status_subquery.values("created_at")[:1]))
            .annotate(
                period=Concat(
                    ExtractYear("working_date"),
                    Value("-"),
                    LPad(ExtractMonth("working_date"), 2, Value("0")),
                    output_field=CharField(),
                )
            )
            .annotate(**quantities_db_annotation())
        )


class Action(models.Model):
    pos_id = models.CharField(
        verbose_name="N° de POS", max_length=48, unique=True, error_messages={"unique": _("Ce N° de POS existe déjà.")}
    )

    holder = models.ForeignKey(
        "core.Entity", on_delete=models.PROTECT, verbose_name="Entité détentrice de la quantité de l'action"
    )

    H2 = "H2"
    INDUSTRIES = [(H2, "Hydrogène")]
    industry = models.CharField(verbose_name="Filière", choices=INDUSTRIES, max_length=16)

    INIT = "INIT"
    VALORIZE = "VALORIZE"
    TYPES = [(INIT, "INIT"), (VALORIZE, "VALORIZE")]
    type = models.CharField(verbose_name="Type d'action", choices=TYPES, max_length=16)

    # Duplicated from Entity.UNIT_CHOICE: sharing is impractical (different contexts).
    L = "l"
    KG = "kg"
    MJ = "MJ"
    UNIT_CHOICE = ((L, "litres"), (KG, "kg"), (MJ, "MJ"))
    unit = models.CharField(verbose_name="Unité", choices=UNIT_CHOICE, max_length=8)

    parent = models.ForeignKey(
        "self", verbose_name="Action parente", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )

    material = models.ForeignKey("traceability.Material", on_delete=models.PROTECT, verbose_name="Matière", null=True)

    certificate = models.ForeignKey(
        "core.GenericCertificate",
        on_delete=models.PROTECT,
        verbose_name="Certificat",
        null=True,
        blank=True,
        related_name="actions",
    )

    quantity = models.DecimalField(verbose_name="Quantité de matière", max_digits=13, decimal_places=3)
    lhv = models.DecimalField(
        verbose_name="PCI (MJ/kg)",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )
    density = models.DecimalField(
        verbose_name="Masse volumique (kg/l)",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )

    site = models.ForeignKey("transactions.Site", on_delete=models.PROTECT, verbose_name="Site", null=True)

    shipping_date = models.DateField(verbose_name="Date d'expédition", blank=True, null=True)
    shipping_distance = models.IntegerField(verbose_name="Distance de livraison", blank=True, null=True)

    ROAD = "ROAD"
    PIPELINE = "PIPELINE"
    RAILROAD = "RAILROAD"
    SEA = "SEA"
    SHIPPING_METHODS = [
        (ROAD, _("Transport routier")),
        (PIPELINE, _("Pipeline")),
        (RAILROAD, _("Rail")),
        (SEA, _("Transport maritime")),
    ]
    shipping_method = models.CharField(
        verbose_name="Mode de transport", choices=SHIPPING_METHODS, max_length=16, null=True, blank=True
    )

    working_date = models.DateField(verbose_name="Date de référence")

    eec = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    el = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    ei = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    ep = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    etd = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eu = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eccs = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    esca = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eccr = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)

    objects = ActionManager()
    unannotated = models.Manager()

    @staticmethod
    @transaction.atomic
    def bulk_create(actions: list["Action"], default_status=ActionStatus.CREATED) -> QuerySet["Action"]:
        Action.objects.bulk_create(actions)
        created_actions = Action.objects.filter(pos_id__in=[a.pos_id for a in actions])

        created_statuses = [ActionStatus(status=default_status, action=a) for a in created_actions]
        ActionStatus.objects.bulk_create(created_statuses)

        return created_actions

    class Meta:
        db_table = "action"
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(lhv__isnull=True) | Q(lhv__gt=0),
                name="action_lhv_null_or_positive",
            ),
            models.CheckConstraint(
                condition=Q(density__isnull=True) | Q(density__gt=0),
                name="action_density_null_or_positive",
            ),
        ]
