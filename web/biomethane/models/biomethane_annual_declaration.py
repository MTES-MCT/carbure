from django.db import models

from core.models import Entity


class BiomethaneAnnualDeclaration(models.Model):
    PENDING = "PENDING"
    VALIDATED = "DECLARED"
    DECLARATION_STATUS = [(PENDING, "PENDING"), (VALIDATED, "DECLARED")]

    # Propriétaire de la déclaration annuelle
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_declarations")

    # Année de déclaration
    year = models.IntegerField()

    status = models.CharField(choices=DECLARATION_STATUS, max_length=20, default=PENDING)

    class Meta:
        db_table = "biomethane_annual_declaration"
        unique_together = ["producer", "year"]
        verbose_name = "Biométhane - Déclaration annuelle"
        verbose_name_plural = "Biométhane - Déclarations annuelles"
