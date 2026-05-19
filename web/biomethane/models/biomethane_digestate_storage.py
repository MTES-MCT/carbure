from django.db import models

from core.models import Entity


class BiomethaneDigestateStorage(models.Model):
    translation_model_key = "digestate_storage"
    # Propriétaire de l'unité de stockage
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_digestate_storage")

    # Type de stockage
    type = models.CharField(verbose_name="Type de stockage", max_length=32)

    # Capacité de stockage (m3)
    capacity = models.FloatField(verbose_name="Capacité de stockage (m3)")

    # Couverture du stockage
    has_cover = models.BooleanField(verbose_name="Couverture du stockage", default=False)

    # Récupération du biogaz
    has_biogas_recovery = models.BooleanField(verbose_name="Récupération du biogaz", default=False)

    class Meta:
        db_table = "biomethane_digestate_storage"
        verbose_name = "Stockage de Digestat"
        verbose_name_plural = "Stockages de Digestat"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)
