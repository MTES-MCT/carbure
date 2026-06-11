from django.db import models


class BiomethaneAnnualDeclarationQuerySet(models.QuerySet):
    def with_computed_status(self):
        if "computed_status" in self.query.annotations:
            return self

        from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService

        return self.annotate(
            computed_status=BiomethaneAnnualDeclarationService.get_declaration_status_annotation(
                "status",
                year_field="year",
            )
        )


class AnnotatedBiomethaneAnnualDeclarationManager(models.Manager):
    def get_queryset(self):
        return BiomethaneAnnualDeclarationQuerySet(self.model, using=self._db).with_computed_status()
