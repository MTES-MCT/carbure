import datetime
from calendar import monthrange
from datetime import date

from django.db import models


class SustainabilityDeclaration(models.Model):
    entity = models.ForeignKey("core.Entity", on_delete=models.CASCADE)
    declared = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    deadline = models.DateField(default=datetime.datetime.now, blank=True)
    period = models.DateField(default=datetime.datetime.now, blank=True)
    reminder_count = models.IntegerField(default=0)

    def natural_key(self):
        return {
            "id": self.id,
            "entity": self.entity.natural_key(),
            "declared": self.declared,
            "period": self.period,
            "deadline": self.deadline,
            "checked": self.checked,
            "month": self.period.month,
            "year": self.period.year,
            "reminder_count": self.reminder_count,
        }

    def init_declaration(entity_id: int, period: int):
        year = int(period / 100)
        month = period % 100
        period_d = datetime.date(year=year, month=month, day=1)
        nextmonth = period_d + datetime.timedelta(days=31)
        (_, lastday) = monthrange(nextmonth.year, nextmonth.month)
        deadline = datetime.date(year=nextmonth.year, month=nextmonth.month, day=lastday)

        declaration, _ = SustainabilityDeclaration.objects.get_or_create(
            entity_id=entity_id,
            period=period_d,
            deadline=deadline,
        )

        return declaration

    class Meta:
        db_table = "declarations"
        verbose_name = " Déclaration de Durabilité"
        verbose_name_plural = " Déclarations de Durabilité"


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
