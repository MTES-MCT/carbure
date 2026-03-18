from django.core.management.base import BaseCommand

from adapters.logger import log_info
from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import UserRights


class Command(BaseCommand):
    help = """
    Check all biomethane annual declarations with status DECLARED and verify if they are complete.

    Usage:
        python web/manage.py check_declared_annual_declarations
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            default=False,
            action="store_true",
            help="Reset incomplete DECLARED declarations to IN_PROGRESS status",
        )

    def handle(self, *args, **options):
        declarations = BiomethaneAnnualDeclaration.objects.filter(
            status=BiomethaneAnnualDeclaration.DECLARED
        ).select_related("producer")

        total = declarations.count()
        complete_count = 0
        incomplete_count = 0
        incomplete_ids = []
        lines = []

        for declaration in declarations:
            producer_name = declaration.producer.name
            admins = UserRights.objects.filter(entity=declaration.producer, role=UserRights.ADMIN).select_related("user")
            emails = [admin.user.email for admin in admins]

            is_complete = BiomethaneAnnualDeclarationService.is_declaration_complete(declaration)

            if is_complete:
                complete_count += 1
                lines.append(f"[COMPLETE]   {producer_name} - {emails}")
                self.stdout.write(self.style.SUCCESS(lines[-1]))
            else:
                incomplete_count += 1
                incomplete_ids.append(declaration.pk)
                lines.append(f"[INCOMPLETE] {producer_name} - {emails}")
                self.stdout.write(self.style.WARNING(lines[-1]))

        summary = f"Summary: {total} checked — {complete_count} complete, {incomplete_count} incomplete."
        self.stdout.write(self.style.SUCCESS(f"\n{summary}"))

        if options["update"]:
            BiomethaneAnnualDeclaration.objects.filter(pk__in=incomplete_ids).update(
                status=BiomethaneAnnualDeclaration.IN_PROGRESS
            )
            update_msg = f"{incomplete_count} incomplete declaration(s) reset to IN_PROGRESS."
            self.stdout.write(self.style.WARNING(update_msg))
            summary += " " + update_msg

        log_info(
            "check_declared_annual_declarations: " + summary,
            additional_infos={"details": "\n".join(lines)},
        )
