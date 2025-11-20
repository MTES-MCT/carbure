"""
Service pour supprimer les certificats orphelins (non reliés à d'autres entités).
"""

import time

from core.models import EntityCertificate, GenericCertificate
from core.services.data_anonymization.utils import delete_queryset_in_batches
from doublecount.models import DoubleCountingSourcingHistory


class OrphanCertificateDeleter:
    DELETE_BATCH_SIZE = 1000

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def delete_orphan_certificates(self):
        start_time = time.perf_counter()

        print("   → Recherche des certificats orphelins...")
        generic_certificates_deleted = self._delete_orphan_generic_certificates()

        elapsed_time = time.perf_counter() - start_time

        if self.dry_run:
            print(
                f"   → [DRY-RUN] Simulation terminée: {generic_certificates_deleted} "
                f"certificats orphelins seraient supprimés"
            )
        else:
            print(f"   → Suppression terminée: {generic_certificates_deleted} certificats orphelins supprimés ")

        return generic_certificates_deleted, elapsed_time

    def _delete_orphan_generic_certificates(self):
        used_by_entity_certs = EntityCertificate.objects.values_list("certificate_id", flat=True).distinct()
        used_by_dc_apps = (
            DoubleCountingSourcingHistory.objects.exclude(supplier_certificate__isnull=True)
            .values_list("supplier_certificate_id", flat=True)
            .distinct()
        )

        # Combiner les IDs utilisés
        used_cert_ids = set(used_by_entity_certs) | set(used_by_dc_apps)

        # Récupérer les certificats orphelins
        orphan_certs = GenericCertificate.objects.exclude(id__in=used_cert_ids)

        count = orphan_certs.count()
        if count == 0:
            print("   → Aucun GenericCertificate orphelin trouvé")
            return 0

        print(f"   → {count} GenericCertificate orphelins trouvés")

        if self.dry_run:
            return count

        return self._delete_in_batches(orphan_certs)

    def _delete_in_batches(self, queryset):
        queryset = queryset.order_by("id")
        return delete_queryset_in_batches(
            queryset=queryset,
            batch_size=self.DELETE_BATCH_SIZE,
            dry_run=self.dry_run,
            item_name="certificats",
        )
