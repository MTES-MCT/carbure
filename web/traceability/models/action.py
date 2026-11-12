from decimal import Decimal

from django.db import models, transaction
from django.db.models import CharField, Q, QuerySet, Value
from django.db.models.functions import Concat, ExtractMonth, ExtractYear, LPad
from django.utils.translation import gettext_lazy as _

from traceability.services.quantities import quantity_available

from .action_status import ActionStatus, latest_status


class ActionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("holder", "material", "site", "parent", "certificate")
            .annotate(status=latest_status())
            .annotate(
                period=Concat(
                    ExtractYear("working_date"),
                    Value("-"),
                    LPad(ExtractMonth("working_date"), 2, Value("0")),
                    output_field=CharField(),
                )
            )
            .annotate(quantity_available=quantity_available())
            .filter(quantity_available__gt=0)
        )


class Action(models.Model):
    pos_id = models.CharField(
        verbose_name="N° de POS", max_length=48, unique=True, error_messages={"unique": _("Ce N° de POS existe déjà.")}
    )

    holder = models.ForeignKey(
        "core.Entity", on_delete=models.PROTECT, verbose_name="Entité détentrice de la quantité de l'action"
    )

    H2 = "H2"
    UNKNOWN = "UNKNOWN"
    INDUSTRIES = [(H2, "Hydrogène"), (UNKNOWN, "Inconnu")]
    industry = models.CharField(verbose_name="Filière", choices=INDUSTRIES, max_length=16)

    INIT = "INIT"
    VALORIZE = "VALORIZE"
    TYPES = [(INIT, "INIT"), (VALORIZE, "VALORIZE")]
    type = models.CharField(verbose_name="Type d'action", choices=TYPES, max_length=16)

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

    file = models.ForeignKey(
        "core.StoredFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions",
        verbose_name="Fichier",
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
    def annotate_actions(actions: list["Action"]) -> list["Action"]:
        """Annotate these actions and return them in the same order.

        The parent walk covers inherited fields and total emissions, and it runs
        only on the given rows. Callers paginate first: MySQL rejects LIMIT inside
        that walk. ``quantity_available`` is already on the manager queryset.
        """
        if not actions:
            return actions

        from traceability.services.inherited_fields import attach_inherited_fields
        from traceability.services.parent_chain import annotate_parent_chain

        ids = [action.pk for action in actions]
        annotated = {action.pk: action for action in annotate_parent_chain(Action.objects.filter(pk__in=ids))}
        ordered = [annotated[pk] for pk in ids]
        attach_inherited_fields(ordered)
        return ordered

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
        indexes = [
            # Years and date ordering always filter by industry and type.
            models.Index(fields=["industry", "type", "working_date"], name="action_industry_type_date"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gt=0), name="action_quantity_positive"),
        ]
