from django.db import models

from core.models import Entity


class BiomethaneAnnualDeclaration(models.Model):
    IN_PROGRESS = "IN_PROGRESS"
    DECLARED = "DECLARED"
    DECLARATION_STATUS = [(IN_PROGRESS, IN_PROGRESS), (DECLARED, DECLARED)]

    # Propriétaire de la déclaration annuelle
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_declarations")

    # Année de déclaration
    year = models.IntegerField()

    status = models.CharField(choices=DECLARATION_STATUS, max_length=20, default=IN_PROGRESS)

    class Meta:
        db_table = "biomethane_annual_declaration"
        unique_together = ["producer", "year"]
        verbose_name = "Biométhane - Déclaration annuelle"
        verbose_name_plural = "Biométhane - Déclarations annuelles"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)
