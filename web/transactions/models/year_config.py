from django.db import models


class YearConfig(models.Model):
    year = models.IntegerField(blank=False, null=False)  # index
    locked = models.BooleanField(default=True, help_text="Bloquer les déclarations")
    renewable_share = models.FloatField(blank=True, null=True, help_text="En pourcentage (ex: 24.92)")  # index

    class Meta:
        db_table = "year_config"
        indexes = [models.Index(fields=["year"])]
        verbose_name = "Configuration annuelle"
        verbose_name_plural = "Configurations annuelles"
