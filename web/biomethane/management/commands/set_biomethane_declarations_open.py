from datetime import date, timedelta

from django.core.management.base import BaseCommand

from biomethane.models import BiomethaneAnnualDeclaration, BiomethaneDeclarationPeriod
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService


class Command(BaseCommand):
    help = """
    Update is_open status for all biomethane annual declarations of current year.

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
        current_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        is_open = options["open"] == "true"

        if not is_open:
            # Check if today is the next day after last day of the declaration period
            if current_declaration_period := BiomethaneDeclarationPeriod.objects.filter(year=current_year).first():
                end_date = current_declaration_period.end_date

                if date.today() != end_date + timedelta(days=1):
                    self.stdout.write(self.style.ERROR("Not today. Nothing to do."))
                    return
            else:
                self.stdout.write(self.style.ERROR(f"Declaration period for year {current_year} does not exist"))
                return

        data = {"is_open": is_open}
        if is_open:
            data["status"] = BiomethaneAnnualDeclaration.IN_PROGRESS

        updated_count = BiomethaneAnnualDeclaration.objects.filter(year=current_year).update(**data)

        status = "open" if is_open else "closed"
        self.stdout.write(
            self.style.SUCCESS(f"Successfully set {updated_count} biomethane annual declaration(s) to {status}")
        )
