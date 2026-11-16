import uuid

from django.db import migrations, models

import traceability.models.action


def fill_carbure_ids(apps, schema_editor):
    Action = apps.get_model("traceability", "Action")
    for action in Action.objects.all():
        action.carbure_id = str(uuid.uuid4())
        action.save(update_fields=["carbure_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0018_actionstatus_action_status_latest"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="carbure_id",
            field=models.CharField(max_length=64, null=True, verbose_name="Identifiant Carbure"),
        ),
        migrations.RunPython(fill_carbure_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="action",
            name="carbure_id",
            field=models.CharField(
                default=traceability.models.action.generate_carbure_id,
                editable=False,
                max_length=64,
                unique=True,
                verbose_name="Identifiant Carbure",
            ),
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
    ]
