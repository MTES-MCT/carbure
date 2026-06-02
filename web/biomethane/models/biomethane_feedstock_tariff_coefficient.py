from django.db import models


class BiomethaneFeedstockTariffCoefficient(models.Model):
    """
    Reference data: tariff coefficient (P1, P2, P3, P, Peff) for a feedstock under a given
    tariff decree regime (extensible granularity, independent of contract TARIFF_RULE groups).
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
    PEFF = "PEFF"

    COEFFICIENT_CHOICES = (
        (P1, "P1"),
        (P2, "P2"),
        (P3, "P3"),
        (P, "P"),
        (PEFF, "Peff"),
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
                fields=["feedstock", "regime"],
                name="unique_feedstock_tariff_coefficient_regime",
            ),
        ]

    def __str__(self):
        return f"{self.feedstock} — {self.get_regime_display()} → {self.coefficient}"

    @classmethod
    def regime_for_tariff_reference(cls, tariff_reference):
        return cls.TARIFF_REFERENCE_TO_REGIME.get(tariff_reference)
