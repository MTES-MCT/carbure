"""
Service to reduce the number of carbure lots.
- Deletes all lots from years with less than 100 lots
- For other years, keeps only 1000 lots per year and deletes the rest.
"""

import time

from django.db import transaction

from core.models import CarbureLot


class CarbureLotDeleter:
    """
    Service to reduce the number of carbure lots in the database.
    """

    # If the number of lots is below this threshold, all lots are deleted
    MIN_LOTS_THRESHOLD = 100

    DELETE_BATCH_SIZE = 1000

    def __init__(self, limit=1000, dry_run=False):
        """
        Initialize the deletion service.

        Args:
            limit: Number of lots to keep per year (default: 1000)
            dry_run: If True, simulates deletion without modifying data
        """
        self.limit = 1000
        self.dry_run = dry_run

    def execute(self):
        """
        Execute the deletion of carbure lots according to the defined rules.

        Returns:
            tuple: (number_of_lots_kept, number_of_lots_deleted, elapsed_time)
        """
        start_time = time.perf_counter()

        years = self._get_years_to_process()
        if not years:
            print("   → Aucun lot trouvé dans la base de données.")
            elapsed_time = time.perf_counter() - start_time
            return 0, 0, elapsed_time

        stats_by_year, total_to_keep, total_to_delete = self._calculate_statistics_by_year(years)
        self._display_statistics(stats_by_year, total_to_keep, total_to_delete)

        if total_to_delete == 0:
            print("   → Aucun lot à supprimer. Tous les lots sont déjà dans la limite.")
            elapsed_time = time.perf_counter() - start_time
            return total_to_keep, 0, elapsed_time

        kept_count, deleted_count = self._delete_lots_by_statistics(stats_by_year)
        self._display_final_summary(total_to_keep, total_to_delete, kept_count, deleted_count)

        elapsed_time = time.perf_counter() - start_time
        if self.dry_run:
            return total_to_keep, total_to_delete, elapsed_time
        else:
            return kept_count, deleted_count, elapsed_time

    def _get_years_to_process(self):
        """Get the list of years to process."""
        return CarbureLot.objects.values_list("year", flat=True).distinct().order_by("year")

    def _calculate_statistics_by_year(self, years):
        """
        Calculate the statistics of deletion by year.

        Returns:
            tuple: (stats_by_year, total_to_keep, total_to_delete)
        """
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

        return stats_by_year, total_to_keep, total_to_delete

    def _display_statistics(self, stats_by_year, total_to_keep, total_to_delete):
        """Display the statistics by year."""
        print("   → Statistiques par année:")
        for stat in stats_by_year:
            if stat["will_be_deleted"]:
                print(
                    f"     • Année {stat['year']}: {stat['total']} lots → TOUS SUPPRIMÉS "
                    f"(< {self.MIN_LOTS_THRESHOLD} lots)"
                )
            else:
                print(
                    f"     • Année {stat['year']}: {stat['total']} lots "
                    f"→ {stat['to_keep']} conservés, {stat['to_delete']} supprimés"
                )
        print(f"   → Total: {total_to_keep} à garder, {total_to_delete} à supprimer")

    def _delete_lots_by_statistics(self, stats_by_year):
        """
        Delete lots according to the calculated statistics.

        Returns:
            tuple: (kept_count, deleted_count)
        """
        deleted_count = 0
        kept_count = 0

        for stat in stats_by_year:
            if stat["to_delete"] == 0:
                kept_count += stat["to_keep"]
                continue

            kept, deleted = self._process_year(stat)
            kept_count += kept
            deleted_count += deleted

        return kept_count, deleted_count

    def _display_final_summary(self, total_to_keep, total_to_delete, kept_count, deleted_count):
        """Display the final summary of the operation."""
        if self.dry_run:
            print(
                f"   → [DRY-RUN] Simulation terminée: {total_to_delete} lots seraient supprimés, "
                f"{total_to_keep} lots seraient conservés"
            )
        else:
            print(f"   → Suppression terminée: {deleted_count} lots supprimés, {kept_count} lots conservés")

    def _process_year(self, stat):
        """Processes a year by deleting excess lots in batches."""
        year = stat["year"]
        to_delete = stat["to_delete"]

        print(f"     Année {year}: {stat['total']} lots au total")

        if stat["will_be_deleted"]:
            # Delete all lots from the year
            print(f"       → Complete deletion (year with < {self.MIN_LOTS_THRESHOLD} lots)")
            if self.dry_run:
                return 0, to_delete
            else:
                lots_to_delete = CarbureLot.objects.filter(year=year).order_by("id")
                deleted = self._delete_in_batches(lots_to_delete)
                return 0, deleted
        else:
            # Delete lots beyond the limit
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
        Deletes lots in batches to avoid memory and lock issues.

        Args:
            queryset: QuerySet of lots to delete

        Returns:
            int: Total number of lots deleted
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

        # Use iterator to process queryset in chunks without loading everything into memory
        batch_ids = []
        batch_num = 0
        processed_count = 0

        for obj in queryset.iterator(chunk_size=self.DELETE_BATCH_SIZE):
            batch_ids.append(obj.id)
            processed_count += 1

            # Process batch when size is reached or when we've processed all items
            if len(batch_ids) >= self.DELETE_BATCH_SIZE or processed_count >= total_to_delete:
                batch_num += 1
                with transaction.atomic():
                    deleted_count = self._delete_lots_by_batch(batch_ids, batch_num, total_batches)
                    total_deleted += deleted_count
                batch_ids = []

        print(f"       Total supprimé: {total_deleted} lots (sur {total_to_delete} attendus)")
        return total_deleted

    def _delete_lots_by_batch(self, batch_ids, current_batch, total_batches):
        deleted = CarbureLot.objects.filter(id__in=batch_ids).delete()
        deleted_count = deleted[1].get("core.CarbureLot", 0)

        print(
            f"         Batch {current_batch}/{total_batches}: {deleted_count} lots supprimés "
            f"(sur {len(batch_ids)} attendus)"
        )

        return deleted_count
