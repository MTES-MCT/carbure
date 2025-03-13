from django.db import models


class FossilFuel(models.Model):
    label = models.CharField(max_length=255)
    fuel_category = models.ForeignKey(
        "tiruert.FossilFuelCategory", null=True, on_delete=models.SET_NULL, related_name="fossil_fuels"
    )
    pci_litre = models.FloatField(default=0.0)
    masse_volumique = models.FloatField(default=0.0)
    nomenclatures = models.JSONField(default=list)

    def __str__(self):
        return self.label

    class Meta:
        db_table = "fossil_fuels"
        verbose_name = "Fossil Fuel"
        verbose_name_plural = "Fossil Fuels"
