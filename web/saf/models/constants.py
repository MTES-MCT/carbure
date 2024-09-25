from django.db import models


class TicketStatus(models.TextChoices):
    PENDING = "PENDING", "En attente"
    ACCEPTED = "ACCEPTED", "Accepté"
    REJECTED = "REJECTED", "Refusé"
