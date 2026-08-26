from decimal import Decimal

from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from .action_status import ActionStatus


class ActionManager(models.Manager):
    def get_queryset(self):
        first_status_subquery = ActionStatus.objects.filter(action=OuterRef("id")).order_by("created_at", "id")
        latest_status_subquery = ActionStatus.objects.filter(action=OuterRef("id")).order_by("-created_at", "-id")

        return (
            super()
            .get_queryset()
            .select_related("holder", "material", "site", "parent")
            .annotate(status=Subquery(latest_status_subquery.values("status")[:1]))
            .annotate(created_at=Subquery(first_status_subquery.values("created_at")[:1]))
            .annotate(updated_at=Subquery(latest_status_subquery.values("created_at")[:1]))
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
    TYPES = [(INIT, "INIT")]
    type = models.CharField(verbose_name="Type d'action", choices=TYPES, max_length=16)

    parent = models.ForeignKey(
        "self", verbose_name="Action parente", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )

    material = models.ForeignKey("traceability.Material", on_delete=models.PROTECT, verbose_name="Matière")

    # Quantity in MJ
    quantity = models.DecimalField(verbose_name="Quantité de matière", max_digits=13, decimal_places=3)

    site = models.ForeignKey("transactions.Site", on_delete=models.PROTECT, verbose_name="Site")

    shipping_date = models.DateField(verbose_name="Date d'expédition")
    shipping_distance = models.IntegerField(verbose_name="Distance de livraison")

    ROAD = "ROAD"
    PIPELINE = "PIPELINE"
    RAILROAD = "RAILROAD"
    SEA = "SEA"
    SHIPPING_METHODS = [(ROAD, "Transport routier"), (PIPELINE, "Pipeline"), (RAILROAD, "Rail"), (SEA, "Transport maritime")]
    shipping_method = models.CharField(verbose_name="Mode de transport", choices=SHIPPING_METHODS, max_length=16)

    working_date = models.DateField(verbose_name="Date de référence")

    ei = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    ep = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    etd = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eu = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eccs = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)

    objects = ActionManager()

    class Meta:
        db_table = "action"
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        ordering = ["id"]
