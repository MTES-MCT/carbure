from datetime import date

from django.db import models


class DeclarationPeriod(models.Model):
    """
    Generic declaration period model that defines opening/closing dates for annual declarations.
    """

    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    BIOMETHANE = "BIOMETHANE"
    TIRUERT = "TIRUERT"
    APPS = (
        (BIOMETHANE, BIOMETHANE),
        (TIRUERT, TIRUERT),
    )
    app = models.CharField(max_length=20, choices=APPS, default=BIOMETHANE)

    class Meta:
        db_table = "declaration_periods"
        verbose_name = "Période de déclaration"
        verbose_name_plural = "Périodes de déclaration"
        models.UniqueConstraint(
            fields=["year", "app"],
            name="unique_year_per_app",
        )

    @property
    def is_open(self):
        today = date.today()
        return self.start_date <= today <= self.end_date
