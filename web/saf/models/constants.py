from django.db import models

SAF_BIOFUEL_TYPES = ("HVOC", "HOC", "HCC")


class TicketStatus(models.TextChoices):
    PENDING = "PENDING", "En attente"
    ACCEPTED = "ACCEPTED", "Accepté"
    REJECTED = "REJECTED", "Refusé"
