from django.core.management.base import BaseCommand

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService


class Command(BaseCommand):
    help = """
    Update is_open status for all biomethane annual declarations.

    Usage:
        python web/manage.py set_biomethane_declarations_open --open=true
        python web/manage.py set_biomethane_declarations_open --open=false
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--open",
            type=str,
            required=True,
            choices=["true", "false"],
            help="Set declarations as open (true) or closed (false)",
        )

    def handle(self, *args, **options):
        is_open = options["open"] == "true"

        year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        updated_count = BiomethaneAnnualDeclaration.objects.filter(year=year).update(is_open=is_open)

        status = "open" if is_open else "closed"
        self.stdout.write(
            self.style.SUCCESS(f"Successfully set {updated_count} biomethane annual declaration(s) to {status}")
        )
