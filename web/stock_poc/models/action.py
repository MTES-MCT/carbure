from django.db import models

from core.models import Entity
from stock_poc.managers import ActionManager


class Action(models.Model):
    """Node of the stock tree POC.

    Each action represents a quantity of matter (physical) or of certificate
    (accounting) that derives from its parent action. The available balance of
    an action is `quantity - sum(direct children whose latest status is not REFUSED)`.
    """

    # Action types under test for the POC
    CREATION_H2 = "CREATION_H2"
    TRANSFERT = "TRANSFERT"
    CONSOMMATION = "CONSOMMATION"
    PERTE = "PERTE"
    VALORISATION = "VALORISATION"
    TYPES = [
        (CREATION_H2, CREATION_H2),
        (TRANSFERT, TRANSFERT),
        (CONSOMMATION, CONSOMMATION),
        (PERTE, PERTE),
        (VALORISATION, VALORISATION),
    ]

    quantity = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Quantité")
    type = models.CharField(max_length=32, choices=TYPES, verbose_name="Type d'action")
    owner = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="stock_poc_actions",
        verbose_name="Entité propriétaire",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="Action parente",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ActionManager()

    class Meta:
        db_table = "stock_poc_action"
        verbose_name = "Action (stock POC)"
        verbose_name_plural = "Actions (stock POC)"
        ordering = ["id"]

    def __str__(self):
        return f"#{self.pk} {self.type} {self.quantity} - {self.owner_id}"
