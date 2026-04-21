from django.db import models

from biomethane.models import BiomethaneEnergy
from core.models.virtual_fields import virtual_field


class BiomethaneEnergyMonthlyReport(models.Model):
    translation_model_key = "energy.monthly_report"
    # Production d'énergie associée
    energy = models.ForeignKey(BiomethaneEnergy, on_delete=models.CASCADE, related_name="monthly_reports")
    # Mois du relevé (1-12)
    month = models.IntegerField(verbose_name="Mois")
    # Volume injecté (Nm3)
    injected_volume_nm3 = models.FloatField(default=0, verbose_name="Volume injecté (Nm3)")
    # Débit moyen mensuel (Nm3/h)
    average_monthly_flow_nm3_per_hour = models.FloatField(default=0, verbose_name="Débit moyen mensuel (Nm3/h)")

    class Meta:
        db_table = "biomethane_energy_monthly_report"
        verbose_name = "Énergie - Relevés mensuels Biométhane injecté"

    @property
    def production_unit(self):
        if hasattr(self, "energy") and self.energy:
            return getattr(self.energy.producer, "biomethane_production_unit", None)
        return None

    @virtual_field(verbose_name="Heures d'injection (h)")
    def injection_hours(self):
        if not self.injected_volume_nm3 or not self.average_monthly_flow_nm3_per_hour:
            return 0
        return round(self.injected_volume_nm3 / self.average_monthly_flow_nm3_per_hour, 2)
