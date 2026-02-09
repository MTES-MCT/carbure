from django.db import models


class SafLogistics(models.Model):
    """
    Ce modèle représente des contraintes de livraison de SAF.
    Il spécifie pour un dépôt d'origine donné quels modes de transport sont disponibles
    et quels aéroports sont atteignables avec ces contraintes.
    """

    class Meta:
        db_table = "saf_logistics"
        verbose_name = "Logistique SAF"
        verbose_name_plural = "Logistiques SAF"
        ordering = ["created_at"]

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    origin_depot = models.ForeignKey(
        "transactions.Depot",
        related_name="depot_to_airport_routes",
        null=True,
        on_delete=models.CASCADE,
    )

    destination_airport = models.ForeignKey(
        "transactions.Airport",
        related_name="airport_from_depot_routes",
        null=True,
        on_delete=models.CASCADE,
    )

    # quand True, signifie qu'il y a une dernière étape entre le point d'arrivée du mode de transport sélectionné
    # et l'aéroport de destination, qui sera effectuée en routier.
    has_intermediary_depot = models.BooleanField(default=False)

    TRUCK = "TRUCK"
    BARGE = "BARGE"
    TRAIN = "TRAIN"
    SHIP = "SHIP"
    PIPELINE = "PIPELINE"
    PIPELINE_DMM = "PIPELINE_DMM"
    PIPELINE_LHP = "PIPELINE_LHP"
    PIPELINE_ODC = "PIPELINE_ODC"
    PIPELINE_SPMR = "PIPELINE_SPMR"
    PIPELINE_SPSE = "PIPELINE_SPSE"

    SHIPPING_METHODS = [
        (TRUCK, "Routier"),
        (BARGE, "Barge"),
        (TRAIN, "Train"),
        (SHIP, "Bateau"),
        (PIPELINE, "Oléoduc"),
        (PIPELINE_DMM, "Oléoduc DMM"),
        (PIPELINE_LHP, "Oléoduc LHP"),
        (PIPELINE_ODC, "Oléoduc ODC"),
        (PIPELINE_SPMR, "Oléoduc SPMR"),
        (PIPELINE_SPSE, "Oléoduc SPSE"),
    ]

    # Devrait-on convertir ce champ en une foreign key vers un autre modèle plutôt que hardcoder les choix ?
    shipping_method = models.CharField(
        max_length=16,
        choices=SHIPPING_METHODS,
    )
