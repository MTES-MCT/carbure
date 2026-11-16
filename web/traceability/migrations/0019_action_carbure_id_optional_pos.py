import uuid

from django.db import migrations, models


def fill_carbure_ids(apps, schema_editor):
    Action = apps.get_model("traceability", "Action")
    for action in Action.objects.all():
        action.carbure_id = uuid.uuid4()
        action.save(update_fields=["carbure_id"])


def clear_valorize_pos_ids(apps, schema_editor):
    """Valorize used to store a generated UUID in pos_id. That number is not a PoS."""
    Action = apps.get_model("traceability", "Action")
    Action.objects.filter(type="VALORIZE").update(pos_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0018_actionstatus_action_status_latest"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="carbure_id",
            field=models.UUIDField(null=True, verbose_name="Identifiant Carbure"),
        ),
        migrations.RunPython(fill_carbure_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="action",
            name="carbure_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Identifiant Carbure"),
        ),
        migrations.AlterField(
            model_name="action",
            name="pos_id",
            field=models.CharField(
                blank=True,
                error_messages={"unique": "Ce N° de POS existe déjà."},
                max_length=48,
                null=True,
                unique=True,
                verbose_name="N° de POS",
            ),
        ),
        migrations.RunPython(clear_valorize_pos_ids, migrations.RunPython.noop),
    ]
