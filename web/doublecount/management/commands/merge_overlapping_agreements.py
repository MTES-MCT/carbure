import warnings
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from doublecount.models import DoubleCountingApplication, DoubleCountingProduction, DoubleCountingSourcing


class Command(BaseCommand):
    help = """
    Merge two overlapping DC declarations.
    The contents of the first year of the newer declaration will be transferred as 2nd year of the older one.
    The older declaration will be set as PENDING again in order to revalidate quotas.
    The newer declaration will be set as REJECTED.

    Usage: python web/manage.py merge_overlapping_agreements --ids=<older_agreement_number>,<newer_agreement_number>
    """

    warnings.simplefilter("ignore", UserWarning)

    def add_arguments(self, parser):
        parser.add_argument("--ids", type=str, help="DCA certificate ids, separated by a comma")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["ids"]:
            ids = options["ids"].split(",")
            older_dca = DoubleCountingApplication.objects.get(certificate_id=ids[0])
            newer_dca = DoubleCountingApplication.objects.get(certificate_id=ids[1])
            overlapping_applications = [(older_dca, newer_dca)]
        else:
            overlapping_applications = self.get_overlapping_applications()

        for older_dca, newer_dca in overlapping_applications:
            self.merge_overlapping_agreements(older_dca, newer_dca)

    def get_overlapping_applications(self):
        applications = DoubleCountingApplication.objects.exclude(status="REJECTED").order_by("period_start")

        app_by_psite = defaultdict(list)
        for a in applications:
            app_by_psite[a.production_site.name].append(a)

        overlapping_applications = []
        for psite in app_by_psite:
            apps = app_by_psite[psite]
            for app in apps:
                year = app.period_start.year
                apps.remove(app)
                for other_app in apps:
                    other_year = other_app.period_start.year
                    if abs(other_year - year) == 1:
                        overlapping_applications.append((app, other_app))

        return overlapping_applications

    def merge_overlapping_agreements(self, older_dca: DoubleCountingApplication, newer_dca: DoubleCountingApplication):
        overlapping_year = newer_dca.period_start.year

        # get all newer application details for overlapping year
        newer_sourcing = DoubleCountingSourcing.objects.filter(dca=newer_dca, year=overlapping_year)
        newer_production = DoubleCountingProduction.objects.filter(dca=newer_dca, year=overlapping_year)

        # check changes in sourcing
        sourcing_to_move: list[DoubleCountingSourcing] = []
        for sourcing in newer_sourcing:
            sourcing.dca = older_dca
            sourcing_to_move.append(sourcing)
        DoubleCountingSourcing.objects.bulk_update(sourcing_to_move, ["dca"])

        # check changes in production
        production_to_move: list[DoubleCountingProduction] = []
        for production in newer_production:
            production.dca = older_dca
            production_to_move.append(production)
        DoubleCountingProduction.objects.bulk_update(production_to_move, ["dca"])

        older_dca.status = DoubleCountingApplication.PENDING
        older_dca.save()

        newer_dca.status = DoubleCountingApplication.REJECTED
        newer_dca.save()
