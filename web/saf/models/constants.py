from django.db import models

from transactions.models.depot import Depot

SAF_BIOFUEL_TYPES = ("HVOC", "HOC", "HCC")

SAF_DEPOT_TYPES = [Depot.EFS, Depot.EFCA]


class TicketStatus(models.TextChoices):
    PENDING = "PENDING", "En attente"
    ACCEPTED = "ACCEPTED", "Accepté"
    REJECTED = "REJECTED", "Refusé"
