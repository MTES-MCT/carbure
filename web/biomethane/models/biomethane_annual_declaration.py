from django.db import models

from biomethane.models.managers.biomethane_annual_declaration import AnnotatedBiomethaneAnnualDeclarationManager
from core.models import Entity


class BiomethaneAnnualDeclaration(models.Model):
    IN_PROGRESS = "IN_PROGRESS"
    DECLARED = "DECLARED"
    OVERDUE = "OVERDUE"  # Virtual status
    NOT_STARTED = "NOT_STARTED"  # Virtual status (no declaration row yet)
    DECLARATION_STATUS = [(IN_PROGRESS, IN_PROGRESS), (DECLARED, DECLARED)]
    DECLARATION_STATUS_CHOICES = [
        (IN_PROGRESS, IN_PROGRESS),
        (DECLARED, DECLARED),
        (OVERDUE, OVERDUE),
        (NOT_STARTED, NOT_STARTED),
    ]
    ADMIN_DASHBOARD_STATUS_CHOICES = DECLARATION_STATUS_CHOICES
    # Propriétaire de la déclaration annuelle
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_declarations")

    # Année de déclaration
    year = models.IntegerField()

    status = models.CharField(choices=DECLARATION_STATUS, max_length=20, default=IN_PROGRESS)

    # Indique si la déclaration est modifiable ou non
    is_open = models.BooleanField(default=True)

    submission_date = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()
    annotated_objects = AnnotatedBiomethaneAnnualDeclarationManager()

    class Meta:
        db_table = "biomethane_annual_declaration"
        unique_together = ["producer", "year"]
        verbose_name = "Déclaration annuelle"
        verbose_name_plural = "Déclarations annuelles"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)
