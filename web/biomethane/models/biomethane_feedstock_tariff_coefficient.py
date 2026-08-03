from django.db import models

from .biomethane_supply_input import BiomethaneSupplyInput


class BiomethaneFeedstockTariffCoefficient(models.Model):
    """
    Reference data: tariff coefficient (P1, P2, P3, P, Pef) for a feedstock under a given
    tariff decree regime.

    Optional collection_type discriminates conditional primes (e.g. LOCAL → P1, IAA → P2).
    Empty string means an unconditional rule for that feedstock × regime.
    """

    AT_2011 = "AT_2011"
    AT_2020_PLUS = "AT_2020_PLUS"

    REGIME_CHOICES = (
        (AT_2011, "Tariff decree reference 2011"),
        (AT_2020_PLUS, "Tariff decree reference 2020/21/23"),
    )

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P = "P"
    PEF = "PEF"

    COEFFICIENT_CHOICES = (
        (P1, "P1"),
        (P2, "P2"),
        (P3, "P3"),
        (P, "P"),
        (PEF, "Pef"),
    )

    TARIFF_REFERENCE_TO_REGIME = {
        "2011": AT_2011,
        "2020": AT_2020_PLUS,
        "2021": AT_2020_PLUS,
        "2023": AT_2020_PLUS,
    }

    feedstock = models.ForeignKey(
        "core.MatierePremiere",
        verbose_name="Feedstock",
        on_delete=models.CASCADE,
        related_name="tariff_coefficients",
    )
    regime = models.CharField(
        verbose_name="Tariff decree regime",
        max_length=16,
        choices=REGIME_CHOICES,
    )
    # Empty string = unconditional rule. Not NULL: MySQL UNIQUE cannot enforce
    # uniqueness of NULL values (NULL is never equal to NULL).
    collection_type = models.CharField(
        verbose_name="Type de collecte",
        max_length=10,
        choices=BiomethaneSupplyInput.COLLECTION_TYPE_CHOICES,
        blank=True,
        default="",
    )
    coefficient = models.CharField(
        verbose_name="Coefficient",
        max_length=4,
        choices=COEFFICIENT_CHOICES,
    )

    class Meta:
        db_table = "biomethane_feedstock_tariff_coefficient"
        verbose_name = "Feedstock tariff coefficient"
        verbose_name_plural = "Feedstock tariff coefficients"
        constraints = [
            models.UniqueConstraint(
                fields=["feedstock", "regime", "collection_type"],
                name="unique_feedstock_tariff_coefficient_regime_collection",
            ),
        ]

    def __str__(self):
        collection = self.collection_type or "default"
        return f"{self.feedstock} — {self.get_regime_display()} [{collection}] → {self.coefficient}"

    @classmethod
    def regime_for_tariff_reference(cls, tariff_reference):
        return cls.TARIFF_REFERENCE_TO_REGIME.get(tariff_reference)
