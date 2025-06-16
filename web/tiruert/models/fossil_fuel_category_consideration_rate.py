from django.db import models


class ConsdiderationRateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("category_fuel")


class FossilFuelCategoryConsiderationRate(models.Model):
    category_fuel = models.ForeignKey(
        "tiruert.FossilFuelCategory", on_delete=models.CASCADE, related_name="consideration_rates"
    )
    consideration_rate = models.FloatField(blank=True, null=True, help_text="saisir 0,50 pour 50%")
    year = models.IntegerField()

    class Meta:
        db_table = "fossil_fuel_categories_consideration_rates"
        verbose_name = "Consideration Rate for Fossil Fuel Category"
        verbose_name_plural = "Condideration Rates for Fossil Fuel Categories"

    objects = ConsdiderationRateManager()
