from django.core.management.base import BaseCommand

from core.models import CarbureLot
from core.traceability import bulk_update_traceability_nodes, get_traceability_nodes


class Command(BaseCommand):
    # command: python web/manage.py propagate_saf_origin
    help = "Updates SAF tickets and sources by grabbing the origin lot and depot from the ancestor lot"

    def handle(self, *args, **options):
        saf_lots = CarbureLot.objects.filter(safticketsource__isnull=False)

        nodes = get_traceability_nodes(saf_lots)

        updated_nodes = []
        for node in nodes:
            updated_nodes += node.propagate()

        bulk_update_traceability_nodes(updated_nodes)
