import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from elec.models import ElecProvisionCertificateQualicharge
from elec.services.qualicharge import resolve_cpo


class Command(BaseCommand):
    help = """"
    Retry CPO assignment for Qualicharge certificates with unknown_siren and no cpo

    Command : python web/manage.py relink_qualicharge_unknown_siren --apply
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Apply updates. By default, runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        apply_updates = options["apply"]

        problematic = ElecProvisionCertificateQualicharge.objects.filter(
            cpo__isnull=True, unknown_siren__isnull=False
        ).exclude(unknown_siren="")

        siren_counts = dict(
            problematic.values("unknown_siren").annotate(count=Count("id")).values_list("unknown_siren", "count")
        )

        resolved = {}
        unresolved_sirens = []
        for unknown_siren in siren_counts:
            cpo, _ = resolve_cpo(unknown_siren.strip())
            if cpo is not None:
                resolved[unknown_siren] = cpo
            else:
                unresolved_sirens.append(unknown_siren)

        resolvable_certificates = sum(siren_counts[siren] for siren in resolved)
        updated_certificates = 0
        updated_by_cpo = defaultdict(int)

        if apply_updates and resolved:
            with transaction.atomic():
                for unknown_siren, cpo in resolved.items():
                    updated = problematic.filter(unknown_siren=unknown_siren).update(cpo=cpo, unknown_siren=None)
                    updated_certificates += updated
                    updated_by_cpo[str(cpo.id)] += updated

        payload = {
            "dry_run": not apply_updates,
            "total_problematic_certificates": sum(siren_counts.values()),
            "total_problematic_sirens": len(siren_counts),
            "resolvable_sirens": len(resolved),
            "unresolved_sirens": len(unresolved_sirens),
            "resolvable_certificates": resolvable_certificates,
            "updated_certificates": updated_certificates,
            "updated_by_cpo": dict(updated_by_cpo),
            "sample_unresolved_sirens": unresolved_sirens[:20],
        }

        self.stdout.write(
            f"mode={'apply' if apply_updates else 'dry-run'} "
            f"problematic={payload['total_problematic_certificates']} "
            f"resolvable={payload['resolvable_certificates']} "
            f"updated={payload['updated_certificates']}"
        )

        return json.dumps(payload)
