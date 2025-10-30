from django.db import models

from core.models import Entity


class BiomethaneDigestateStorage(models.Model):
    # Propriétaire de l'unité de stockage
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_digestate_storage")

    # Type de stockage
    type = models.CharField(max_length=32)

    # Capacité de stockage (m3)
    capacity = models.FloatField()

    # Couverture du stockage
    has_cover = models.BooleanField(default=False)

    # Récupération du biogaz
    has_biogas_recovery = models.BooleanField(default=False)

    class Meta:
        db_table = "biomethane_digestate_storage"
        verbose_name = "Biométhane - Stockage de Digestat"
        verbose_name_plural = "Biométhane - Stockages de Digestat"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)
