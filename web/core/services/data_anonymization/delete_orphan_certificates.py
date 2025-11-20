"""
Service pour supprimer les certificats orphelins (non reliés à d'autres entités).
"""

import time

from django.core.paginator import Paginator
from django.db import transaction

from core.models import EntityCertificate, GenericCertificate
from doublecount.models import DoubleCountingSourcingHistory


class OrphanCertificateDeleter:
    """
    Service pour supprimer les certificats orphelins dans la base de données.
    """

    DELETE_BATCH_SIZE = 1000  # Taille des batches pour les suppressions massives

    def __init__(self, dry_run=False):
        """
        Initialise le service de suppression.

        Args:
            dry_run: Si True, simule la suppression sans modifier les données
        """
        self.dry_run = dry_run

    def delete_orphan_certificates(self):
        """
        Supprime tous les certificats orphelins.

        Returns:
            tuple: (nombre_certificats_supprimés, temps_écoulé)
        """
        start_time = time.perf_counter()

        print("   → Recherche des certificats orphelins...")
        # Supprimer les GenericCertificate orphelins (non référencés par ProductionSiteCertificate)
        generic_certificates_deleted = self._delete_orphan_generic_certificates()

        elapsed_time = time.perf_counter() - start_time

        if self.dry_run:
            print(
                f"   → [DRY-RUN] Simulation terminée: {generic_certificates_deleted} certificats orphelins seraient supprimés"
            )
        else:
            print(f"   → Suppression terminée: {generic_certificates_deleted} certificats orphelins supprimés ")

        return generic_certificates_deleted, elapsed_time

    def _delete_orphan_generic_certificates(self):
        """Supprime les GenericCertificate non référencés par EntityCertificate ou DoubleCountingApplication."""
        # Récupérer tous les GenericCertificate utilisés
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
        """
        Supprime les objets par batch pour éviter les problèmes de mémoire et de verrous.

        Args:
            queryset: QuerySet des objets à supprimer

        Returns:
            int: Nombre total d'objets supprimés
        """
        total_deleted = 0
        model = queryset.model

        queryset = queryset.order_by("id")
        # Utiliser Paginator pour diviser le queryset en batches gérables
        paginator = Paginator(queryset, self.DELETE_BATCH_SIZE)

        # Traiter chaque batch
        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            batch_ids = list(page.object_list.values_list("id", flat=True))

            if batch_ids:
                # Supprimer le batch
                with transaction.atomic():
                    deleted = model.objects.filter(id__in=batch_ids).delete()
                    total_deleted += deleted[0]

        return total_deleted
