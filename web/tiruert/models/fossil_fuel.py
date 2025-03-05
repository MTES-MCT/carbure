from django.db import models


class FossilFuel(models.Model):
    name = models.CharField(max_length=255)
    fuel_category = models.ForeignKey(
        "tiruert.FossilFuelCategory", null=True, on_delete=models.SET_NULL, related_name="fossil_fuels"
    )
    pci_litre = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "fossil_fuels"
        verbose_name = "Fossil Fuel"
        verbose_name_plural = "Fossil Fuels"
