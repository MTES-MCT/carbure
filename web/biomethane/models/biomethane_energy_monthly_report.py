from django.db import models

from biomethane.models import BiomethaneEnergy


class BiomethaneEnergyMonthlyReport(models.Model):
    # Production d'énergie associée
    energy = models.ForeignKey(BiomethaneEnergy, on_delete=models.CASCADE, related_name="monthly_reports")
    # Mois du relevé (1-12)
    month = models.IntegerField()
    # Volume injecté (Nm3)
    injected_volume_nm3 = models.FloatField(default=0)
    # Débit moyen mensuel (Nm3/h)
    average_monthly_flow_nm3_per_hour = models.FloatField(default=0)

    class Meta:
        db_table = "biomethane_energy_monthly_report"
        verbose_name = "Énergie - Relevés mensuels Biométhane injecté"

    @property
    def production_unit(self):
        if hasattr(self, "energy") and self.energy:
            return getattr(self.energy.producer, "biomethane_production_unit", None)
        return None
