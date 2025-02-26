from django.core.management.base import BaseCommand

from transactions.services.anomaly_detection import anomaly_detection


class Command(BaseCommand):
    help = "Trigger anomly detection on biofuels"

    def handle(self, *args, **options):
        anomaly_detection()
