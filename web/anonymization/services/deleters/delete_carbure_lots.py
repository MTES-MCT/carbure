"""
Service to reduce the number of carbure lots.
- Deletes all lots from years with less than 100 lots
- For other years, keeps only 1000 lots per year and deletes the rest.
"""

import time

from core.models import CarbureLot

from ..utils import delete_queryset_in_batches


class CarbureLotDeleter:
    """
    Service to reduce the number of carbure lots in the database.
    """

    # If the number of lots is below this threshold, all lots are deleted
    MIN_LOTS_THRESHOLD = 100

    DELETE_BATCH_SIZE = 1000

    def __init__(self, limit=1000, dry_run=False):
        self.limit = limit
        self.dry_run = dry_run

    def execute(self):
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

            print(f"       → Suppression de {to_delete} lots")

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
        return delete_queryset_in_batches(
            queryset=queryset,
            batch_size=self.DELETE_BATCH_SIZE,
            dry_run=self.dry_run,
            item_name="lots",
        )
