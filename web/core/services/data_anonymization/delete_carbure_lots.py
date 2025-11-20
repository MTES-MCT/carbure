"""
Service pour réduire le nombre de lots de carbure.
- Supprime tous les lots des années ayant moins de 100 lots
- Pour les autres années, garde seulement 1000 lots par année et supprime les autres.
"""

import time

from django.core.paginator import Paginator
from django.db import transaction

from core.models import CarbureLot


class CarbureLotReducer:
    """
    Service pour réduire le nombre de lots de carbure dans la base de données.
    """

    MIN_LOTS_THRESHOLD = 100
    DELETE_BATCH_SIZE = 100  # Taille des batches pour les suppressions massives

    def __init__(self, limit=1000, dry_run=False):
        """
        Initialise le service de réduction.

        Args:
            limit: Nombre de lots à garder par année (défaut: 1000)
            dry_run: Si True, simule la suppression sans modifier les données
        """
        self.limit = 70000
        self.dry_run = dry_run

    def reduce_lots(self):
        """
        Réduit le nombre de lots de carbure selon les règles définies.

        Returns:
            tuple: (nombre_lots_conservés, nombre_lots_supprimés, temps_écoulé)
        """
        start_time = time.perf_counter()

        # Récupérer toutes les années distinctes
        # years = CarbureLot.objects.values_list("year", flat=True).distinct().order_by("year")
        years = [2024]
        if not years:
            print("   → Aucun lot trouvé dans la base de données.")
            elapsed_time = time.perf_counter() - start_time
            return 0, 0, elapsed_time

        # Calculer les statistiques
        stats_by_year = []
        total_to_keep = 0
        total_to_delete = 0

        for year in years:
            count = CarbureLot.objects.filter(year=year).count()

            if count < self.MIN_LOTS_THRESHOLD:
                to_keep = 0
                to_delete = count
            else:
                to_keep = min(self.limit, count)
                to_delete = max(0, count - self.limit)

            total_to_keep += to_keep
            total_to_delete += to_delete
            stats_by_year.append(
                {
                    "year": year,
                    "total": count,
                    "to_keep": to_keep,
                    "to_delete": to_delete,
                    "will_be_deleted": count < self.MIN_LOTS_THRESHOLD,
                }
            )

        # Afficher le résumé par année
        print("   → Statistiques par année:")
        for stat in stats_by_year:
            if stat["will_be_deleted"]:
                print(
                    f"     • Année {stat['year']}: {stat['total']} lots → TOUS SUPPRIMÉS (< {self.MIN_LOTS_THRESHOLD} lots)"
                )
            else:
                print(
                    f"     • Année {stat['year']}: {stat['total']} lots "
                    f"→ {stat['to_keep']} conservés, {stat['to_delete']} supprimés"
                )
        print(f"   → Total: {total_to_keep} à garder, {total_to_delete} à supprimer")

        if total_to_delete == 0:
            print("   → Aucun lot à supprimer. Tous les lots sont déjà dans la limite.")
            elapsed_time = time.perf_counter() - start_time
            return total_to_keep, 0, elapsed_time

        # Supprimer les lots
        deleted_count = 0
        kept_count = 0

        for stat in stats_by_year:
            if stat["to_delete"] == 0:
                kept_count += stat["to_keep"]
                continue

            kept, deleted = self._process_year(stat)
            kept_count += kept
            deleted_count += deleted

        # Résumé final - utiliser les statistiques calculées au début pour plus de précision
        if self.dry_run:
            print(
                f"   → [DRY-RUN] Simulation terminée: {total_to_delete} lots seraient supprimés, "
                f"{total_to_keep} lots seraient conservés"
            )
        else:
            print(f"   → Suppression terminée: {deleted_count} lots supprimés, {kept_count} lots conservés")

        elapsed_time = time.perf_counter() - start_time
        # Retourner les valeurs réelles si on a vraiment supprimé, sinon les valeurs calculées
        if self.dry_run:
            return total_to_keep, total_to_delete, elapsed_time
        else:
            return kept_count, deleted_count, elapsed_time

    def _process_year(self, stat):
        """Traite une année en supprimant les lots excédentaires par batch."""
        year = stat["year"]
        to_delete = stat["to_delete"]

        print(f"     Année {year}: {stat['total']} lots au total")

        if stat["will_be_deleted"]:
            # Supprimer tous les lots de l'année
            print(f"       → Suppression complète (année avec < {self.MIN_LOTS_THRESHOLD} lots)")
            if self.dry_run:
                return 0, to_delete
            else:
                lots_to_delete = CarbureLot.objects.filter(year=year).order_by("id")
                deleted = self._delete_in_batches(lots_to_delete)
                return 0, deleted
        else:
            # Supprimer les lots au-delà de la limite
            if stat["total"] <= self.limit:
                print(f"       → Aucune suppression nécessaire ({stat['total']} <= {self.limit})")
                return stat["total"], 0

            print(f"       → Suppression de {to_delete} lots (garder les {self.limit} premiers)")

            if self.dry_run:
                return self.limit, to_delete
            else:
                all_lots = CarbureLot.objects.filter(year=year).order_by("id")
                last_lot = CarbureLot.objects.filter(year=year).order_by("id")[self.limit - 1 : self.limit].first()
                if last_lot:
                    lots_to_delete = CarbureLot.objects.filter(year=year, id__gt=last_lot.id).order_by("id")
                else:
                    lots_to_delete = all_lots
                deleted = self._delete_in_batches(lots_to_delete)
                return self.limit, deleted

    def _delete_in_batches(self, queryset):
        """
        Supprime les lots par batch pour éviter les problèmes de mémoire et de verrous.

        Args:
            queryset: QuerySet des lots à supprimer

        Returns:
            int: Nombre total de lots supprimés
        """
        total_to_delete = queryset.count()
        if total_to_delete == 0:
            return 0

        if self.dry_run:
            num_batches = ((total_to_delete - 1) // self.DELETE_BATCH_SIZE) + 1
            print(f"       [DRY-RUN] {total_to_delete} lots seraient supprimés en {num_batches} batch(s)")
            return total_to_delete

        total_deleted = 0
        total_batches = ((total_to_delete - 1) // self.DELETE_BATCH_SIZE) + 1

        print(f"       Suppression de {total_to_delete} lots en {total_batches} batch(s)...")

        # Utiliser Paginator pour diviser le queryset en batches gérables
        paginator = Paginator(queryset, self.DELETE_BATCH_SIZE)

        # Traiter chaque batch
        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            batch_ids = [obj.id for obj in page.object_list]

            if batch_ids:
                # Supprimer le batch
                with transaction.atomic():
                    deleted = CarbureLot.objects.filter(id__in=batch_ids).delete()
                    deleted_count = deleted[1].get("core.CarbureLot", 0)
                    total_deleted += deleted_count

                    print(
                        f"         Batch {page_num}/{total_batches}: {deleted_count} lots supprimés "
                        f"(sur {len(batch_ids)} attendus)"
                    )

        print(f"       Total supprimé: {total_deleted} lots (sur {total_to_delete} attendus)")
        return total_deleted
