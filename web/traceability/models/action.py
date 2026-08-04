from decimal import Decimal

from django.db import models


class Action(models.Model):
    H2 = "H2"
    INDUSTRIES = [(H2, "Hydrogène")]
    industry = models.CharField(verbose_name="Filière", choices=INDUSTRIES, max_length=16)

    INIT = "INIT"
    TYPES = [(INIT, "INIT")]
    type = models.CharField(verbose_name="Type d'action", choices=TYPES, max_length=16)

    parent = models.ForeignKey(
        "self", verbose_name="Action parente", null=True, on_delete=models.PROTECT, related_name="children"
    )

    holder = models.ForeignKey("core.Entity", verbose_name="Entité détentrice de la quantité de l'action")

    material = models.ForeignKey("traceability.Material", verbose_name="Matière")
    quantity = models.DecimalField(verbose_name="Quantité de matière", max_digits=13, decimal_places=3)

    site = models.ForeignKey("transactions.Site", verbose_name="Site")
    shipping_date = models.DateField(verbose_name="Date d'expédition")

    ROAD = "ROAD"
    PIPELINE = "PIPELINE"
    RAILROAD = "RAILROAD"
    SEA = "SEA"
    SHIPPING_METHODS = [(ROAD, "Transport routier"), (PIPELINE, "Pipeline"), (RAILROAD, "Rail"), (SEA, "Transport maritime")]
    shipping_method = models.CharField(verbose_name="Mode de transport", choices=SHIPPING_METHODS)

    ei = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    ep = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    etd = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eu = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
    eccs = models.DecimalField(default=Decimal(0.0), max_digits=7, decimal_places=3)
