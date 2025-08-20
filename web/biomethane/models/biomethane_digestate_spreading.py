from django.db import models

from .biomethane_digestate import BiomethaneDigestate


class BiomethaneDigestateSpreading(models.Model):
    digestate = models.ForeignKey(BiomethaneDigestate, on_delete=models.CASCADE, related_name="spreading")
    spreading_department = models.CharField(max_length=3)  # Département d'épandage
    spread_quantity = models.FloatField()  # Quantité épandue (t)
    spread_parcels_area = models.FloatField()  # Superficie des parcelles épandues (ha)

    class Meta:
        db_table = "biomethane_digestate_spreading"
        verbose_name = "Données d'épandage du digestat"
