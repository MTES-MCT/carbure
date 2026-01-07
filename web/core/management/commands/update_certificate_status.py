from django.core.management.base import BaseCommand
from django.db.models import Case, CharField, F, Value, When
from django.utils import timezone

from core.models import GenericCertificate


class Command(BaseCommand):
    help = "Met à jour le statut des certificats en fonction de la date actuelle"

    def handle(self, *args, **kwargs):
        self.stdout.write("> Updating certificate status...")

        today = timezone.localdate()

        status_case = Case(
            When(valid_from__gt=today, then=Value(GenericCertificate.PENDING)),
            When(valid_until__lt=today, then=Value(GenericCertificate.EXPIRED)),
            default=Value("VALID"),
            output_field=CharField(),
        )

        total_updated = (
            GenericCertificate.objects.annotate(new_status=status_case)
            .filter(status__in=[GenericCertificate.PENDING, GenericCertificate.VALID])
            .exclude(status=F("new_status"))  # ignore certificates that did not change status
            .update(status=F("new_status"), last_status_update=today)
        )

        self.stdout.write(f"> {total_updated} certificates changed")
