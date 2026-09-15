from django.core.validators import MinValueValidator
from django.db import models

from core.models.fields import JSONChoiceField
from transactions.models.site import Site


class H2Station(Site):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    ACCESS_TYPES = [
        (PUBLIC, "Public"),
        (PRIVATE, "Privé"),
    ]

    access_type = models.CharField(
        verbose_name="Nature d'accès au site",
        max_length=8,
        choices=ACCESS_TYPES,
    )

    DP_350_BAR = 350
    DP_700_BAR = 700
    DISTRIBUTION_PRESSURES = [
        (DP_350_BAR, "350 bars"),
        (DP_700_BAR, "700 bars"),
    ]

    distributed_pressure = JSONChoiceField(
        verbose_name="Pression de l'hydrogène distribué",
        choices=DISTRIBUTION_PRESSURES,
        default=list,
    )

    has_personal_vehicle_connector = models.BooleanField(
        verbose_name="Connecteurs compatibles avec les véhicules particuliers", default=False
    )

    has_compliant_measuring_instruments = models.BooleanField(
        verbose_name="Instruments de mesure de la masse d'H2 conformes au décret 2001-387",
        default=False,
    )

    storage_capacity = models.IntegerField(verbose_name="Capacité de stockage sur site", validators=[MinValueValidator(1)])

    distribution_capacity = models.IntegerField(verbose_name="Capacité de distribution", validators=[MinValueValidator(1)])
