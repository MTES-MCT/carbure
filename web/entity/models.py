from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import Department, Entity
from transactions.models import Depot


class EntityScope(models.Model):
    """
    Defines the scope/perimeter accessible by an entity.
    Can link to departments, depots, or any other model in the future.
    """

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="scopes")

    # Generic relation fields
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "entity_scopes"
        unique_together = [["entity", "content_type", "object_id"]]
        indexes = [
            models.Index(fields=["entity", "content_type"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
        verbose_name = "Entity Scope"
        verbose_name_plural = "Entity Scopes"


class EntityScopeDepartmentManager(models.Manager):
    """Manager that filters EntityScope to only show Department relations"""

    def get_queryset(self):
        qs = super().get_queryset()
        dept_ct = ContentType.objects.get_for_model(Department)
        return qs.filter(content_type=dept_ct)


class EntityScopeDepartment(EntityScope):
    """Proxy model for EntityScope linking to Departments"""

    objects = EntityScopeDepartmentManager()

    class Meta:
        proxy = True
        verbose_name = "Entity Department Scope"
        verbose_name_plural = "Entity Department Scopes"


class EntityScopeDepotManager(models.Manager):
    """Manager that filters EntityScope to only show Depot relations"""

    def get_queryset(self):
        qs = super().get_queryset()
        depot_ct = ContentType.objects.get_for_model(Depot)
        return qs.filter(content_type=depot_ct)


class EntityScopeDepot(EntityScope):
    """Proxy model for EntityScope linking to Depots"""

    objects = EntityScopeDepotManager()

    class Meta:
        proxy = True
        verbose_name = "Entity Depot Scope"
        verbose_name_plural = "Entity Depot Scopes"
