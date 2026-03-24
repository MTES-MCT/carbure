import csv
import io

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
        parser.add_argument(
            "--year",
            type=int,
            help="Year of the declarations to check",
            required=True,
        )

    def handle(self, *args, **options):
        declarations = BiomethaneAnnualDeclaration.objects.filter(
            status=BiomethaneAnnualDeclaration.DECLARED, year=options["year"]
        ).select_related("producer")

        total = declarations.count()
        complete_count = 0
        incomplete_count = 0
        incomplete_ids = []
        lines = []
        csv_rows = []

        for declaration in declarations:
            producer = declaration.producer
            producer_name = producer.name
            admins = UserRights.objects.filter(entity=producer, role=UserRights.ADMIN).select_related("user")
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

                production_unit = getattr(producer, "biomethane_production_unit", None)
                department = production_unit.department if production_unit else None
                managing_external_admins = producer.get_managing_external_admins() or []
                external_admins_emails = []
                for admin_entity in managing_external_admins:
                    external_admins_emails.extend(
                        admin_entity.get_admin_users_emails(user__is_staff=False, user__is_superuser=False)
                    )

                csv_rows.append(
                    {
                        "Nom de l'entité": producer_name,
                        "Emails des admins": ", ".join(sorted(set(emails))),
                        "Département": str(department) if department else "",
                        "Nom DREALS": ", ".join(sorted({entity.name for entity in managing_external_admins})),
                        "Emails DREALS": ", ".join(sorted(external_admins_emails)),
                    }
                )

        summary = f"Summary: {total} checked — {complete_count} complete, {incomplete_count} incomplete."
        self.stdout.write(self.style.SUCCESS(f"\n{summary}"))

        if options["update"]:
            BiomethaneAnnualDeclaration.objects.filter(pk__in=incomplete_ids).update(
                status=BiomethaneAnnualDeclaration.IN_PROGRESS
            )
            update_msg = f"{incomplete_count} incomplete declaration(s) reset to IN_PROGRESS."
            self.stdout.write(self.style.WARNING(update_msg))
            summary += " " + update_msg

        fieldnames = ["Nom de l'entité", "Emails des admins", "Département", "Nom DREALS", "Emails DREALS"]

        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
        log_info(csv_buffer.getvalue())
        log_info(self.style.SUCCESS(f"CSV printed to stdout ({len(csv_rows)} entities)"))
        summary += f" CSV printed to stdout ({len(csv_rows)} entities)."

        log_info(
            "check_declared_annual_declarations: " + summary,
        )
