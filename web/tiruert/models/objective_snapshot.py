from django.db import models

from core.models import Entity


class ObjectiveSnapshot(models.Model):
    """
    Snapshot of computed objectives for a given entity and declaration year.
    Created at the end of a declaration period to freeze the state of objectives.
    Past years are served from this snapshot instead of being recomputed.
    """

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="objective_snapshots")
    year = models.IntegerField()
    date_from = models.DateField()
    date_to = models.DateField()
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tiruert_objective_snapshots"
        unique_together = ("entity", "year")
        verbose_name = "Objective Snapshot"
        verbose_name_plural = "Objective Snapshots"

    def __str__(self):
        return f"ObjectiveSnapshot(entity={self.entity_id}, year={self.year})"
