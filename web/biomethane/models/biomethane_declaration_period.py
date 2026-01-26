from datetime import date

from django.db import models


class BiomethaneDeclarationPeriod(models.Model):
    year = models.IntegerField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "biomethane_declaration_period"
        verbose_name = "Période de déclaration"
        verbose_name_plural = "Périodes de déclaration"

    @property
    def is_open(self):
        today = date.today()
        return self.start_date <= today <= self.end_date
