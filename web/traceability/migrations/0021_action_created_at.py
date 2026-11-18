from django.db import migrations, models
from django.db.models import OuterRef, Subquery
from django.utils import timezone


def fill_created_at_from_oldest_status(apps, schema_editor):
    """Existing actions take the timestamp of their oldest status.

    An action with no status keeps the migration time, so the carbure id always has a year.
    """
    Action = apps.get_model("traceability", "Action")
    ActionStatus = apps.get_model("traceability", "ActionStatus")
    oldest_created_at = (
        ActionStatus.objects.filter(action_id=OuterRef("pk")).order_by("created_at", "id").values("created_at")[:1]
    )
    Action.objects.update(created_at=Subquery(oldest_created_at))
    Action.objects.filter(created_at__isnull=True).update(created_at=timezone.now())


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0020_remove_action_carbure_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="created_at",
            field=models.DateTimeField(null=True, verbose_name="Date de création"),
        ),
        migrations.RunPython(fill_created_at_from_oldest_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="action",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Date de création"),
        ),
    ]
