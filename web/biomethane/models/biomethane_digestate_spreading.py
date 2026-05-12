from django.db import models

from .biomethane_digestate import BiomethaneDigestate


class BiomethaneDigestateSpreading(models.Model):
    digestate = models.ForeignKey(BiomethaneDigestate, on_delete=models.CASCADE, related_name="spreadings")
    spreading_department = models.CharField(verbose_name="Département d'épandage", max_length=3)
    spread_quantity = models.FloatField(verbose_name="Quantité épandue (t)")
    spread_parcels_area = models.FloatField(verbose_name="Superficie des parcelles épandues (ha)")

    class Meta:
        db_table = "biomethane_digestate_spreading"
        verbose_name = "Données d'épandage du digestat"
        verbose_name_plural = "Données d'épandage du digestat"

    @property
    def production_unit(self):
        if hasattr(self, "digestate") and self.digestate:
            return getattr(self.digestate.producer, "biomethane_production_unit", None)
        return None
