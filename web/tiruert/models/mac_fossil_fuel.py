from django.db import models


class MacFossilFuelManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("fuel", "fuel__fuel_category", "operator", "depot")
            .only(
                "fuel_id",
                "operator_id",
                "volume",
                "period",
                "year",
                "depot_id",
                "start_date",
                "end_date",
                "fuel__label",
                "fuel__nomenclature",
                "fuel__fuel_category__name",
                "fuel__fuel_category__pci_litre",
                "fuel__pci_litre",
                "fuel__masse_volumique",
                "operator__name",
                "depot__name",
            )
        )


class MacFossilFuel(models.Model):
    fuel = models.ForeignKey("tiruert.FossilFuel", null=False, on_delete=models.CASCADE, related_name="mac")
    operator = models.ForeignKey("core.Entity", null=False, on_delete=models.CASCADE, related_name="fossil_fuel_mac")
    volume = models.FloatField(default=0.0)
    period = models.IntegerField()
    year = models.IntegerField()
    depot = models.ForeignKey("transactions.Depot", null=True, on_delete=models.SET_NULL, related_name="fossil_fuel_mac")
    start_date = models.DateField()
    end_date = models.DateField()

    objects = MacFossilFuelManager()

    def __str__(self):
        return f"{self.fuel} - {self.operator} - {self.volume} - {self.period} - {self.depot}"

    class Meta:
        db_table = "fossil_fuel_mac"
        verbose_name = "Fossil Fuel MAC"
        verbose_name_plural = "Fossil Fuels MACs"
        # constraints = [
        #    models.UniqueConstraint(
        #        fields=["operator", "fuel", "period"],
        #        name="unicity",
        #    ),
        # ]
