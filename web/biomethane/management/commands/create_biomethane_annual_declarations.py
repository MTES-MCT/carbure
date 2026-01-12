from django.core.management.base import BaseCommand
from django.db import IntegrityError

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity


class Command(BaseCommand):
    help = """
    Create new annual declarations for all biomethane producers for the current declaration year.
    This command should be run on January 1st of each year.

    Usage:
        python web/manage.py create_biomethane_annual_declarations
    """

    def handle(self, *args, **options):
        current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()

        # Get all biomethane producers
        producers = Entity.objects.filter(entity_type=Entity.BIOMETHANE_PRODUCER)

        created_count = 0
        skipped_count = 0

        for producer in producers:
            try:
                BiomethaneAnnualDeclaration.objects.create(
                    producer=producer,
                    year=current_year,
                    status=BiomethaneAnnualDeclaration.IN_PROGRESS,
                    is_open=True,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created declaration for {producer.name} (year {current_year})"))
            except IntegrityError:
                # Declaration already exists for this producer and year
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Declaration already exists for {producer.name} (year {current_year})")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nSummary: {created_count} declaration(s) created, {skipped_count} skipped (already exist)")
        )
