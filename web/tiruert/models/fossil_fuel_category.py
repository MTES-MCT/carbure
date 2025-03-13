from django.db import models


class FossilFuelCategory(models.Model):
    name = models.CharField(max_length=255)
    pci_litre = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "fossil_fuel_categories"
        verbose_name = "Fossil Fuel Category"
        verbose_name_plural = "Fossil Fuels Categories"
