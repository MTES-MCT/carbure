"""
Service pour supprimer les opérations qui ne contiennent pas de détails d'opération.
"""

import time

from django.db.models import Count

from core.services.data_anonymization.utils import delete_queryset_in_batches
from tiruert.models.operation import Operation


class EmptyOperationDeleter:
    """
    Service pour supprimer les opérations sans détails d'opération.
    """

    DELETE_BATCH_SIZE = 1000

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def delete_empty_operations(self):
        """
        Supprime toutes les opérations qui n'ont pas de détails d'opération associés.

        Returns:
            tuple: (nombre_operations_supprimees, temps_ecoule)
        """
        start_time = time.perf_counter()

        print("   → Recherche des opérations sans détails...")
        empty_operations = self._find_empty_operations()

        count = empty_operations.count()
        if count == 0:
            print("   → Aucune opération vide trouvée")
            elapsed_time = time.perf_counter() - start_time
            return 0, elapsed_time

        print(f"   → {count} opérations vides trouvées")

        if self.dry_run:
            print(f"   → [DRY-RUN] Simulation terminée: {count} opérations seraient supprimées")
            elapsed_time = time.perf_counter() - start_time
            return count, elapsed_time

        deleted_count = self._delete_in_batches(empty_operations)
        print(f"   → Suppression terminée: {deleted_count} opérations supprimées")

        elapsed_time = time.perf_counter() - start_time
        return deleted_count, elapsed_time

    def _find_empty_operations(self):
        """
        Trouve toutes les opérations qui n'ont pas de détails d'opération.

        Returns:
            QuerySet: QuerySet des opérations sans détails
        """
        # Utilise une annotation pour compter les détails et filtre celles qui en ont 0
        empty_operations = Operation.objects.annotate(details_count=Count("details")).filter(details_count=0)
        return empty_operations.order_by("id")

    def _delete_in_batches(self, queryset):
        """
        Supprime les opérations en batch pour éviter les problèmes de mémoire et de verrous.

        Args:
            queryset: QuerySet des opérations à supprimer

        Returns:
            int: Nombre total d'opérations supprimées
        """
        return delete_queryset_in_batches(
            queryset=queryset,
            batch_size=self.DELETE_BATCH_SIZE,
            dry_run=self.dry_run,
            item_name="opérations",
        )
