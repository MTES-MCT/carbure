"""
Remove duplicate UserRights rows (keeping the most recent one per user+entity)
then add a unique_together constraint to prevent future duplicates.
"""

from django.db import migrations
from django.db.models import Count, Max


def remove_duplicate_user_rights(apps, schema_editor):
    """For each (user_id, entity_id) group with duplicates, keep only the row with
    the latest date_added and delete the rest."""
    UserRights = apps.get_model("core", "UserRights")

    duplicates = (
        UserRights.objects.values("user_id", "entity_id")
        .annotate(cnt=Count("id"), max_id=Max("id"))
        .filter(cnt__gt=1)
    )

    ids_to_delete = []
    for dup in duplicates:
        # Keep the row with the highest id (most recent), delete others
        older = (
            UserRights.objects.filter(
                user_id=dup["user_id"],
                entity_id=dup["entity_id"],
            )
            .exclude(id=dup["max_id"])
            .values_list("id", flat=True)
        )
        ids_to_delete.extend(older)

    if ids_to_delete:
        UserRights.objects.filter(id__in=ids_to_delete).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0065_region_alter_department_code_dept_department_region"),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_user_rights,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterUniqueTogether(
            name="userrights",
            unique_together={("user", "entity")},
        ),
    ]
