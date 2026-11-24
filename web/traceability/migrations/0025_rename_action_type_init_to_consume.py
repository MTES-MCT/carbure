from django.db import migrations, models


def rename_init_to_consume(apps, schema_editor):
    Action = apps.get_model("traceability", "Action")
    Action.objects.filter(type="INIT").update(type="CONSUME")


def rename_consume_to_init(apps, schema_editor):
    Action = apps.get_model("traceability", "Action")
    Action.objects.filter(type="CONSUME").update(type="INIT")


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0024_alter_action_industry"),
    ]

    operations = [
        migrations.RunPython(rename_init_to_consume, rename_consume_to_init),
        migrations.AlterField(
            model_name="action",
            name="type",
            field=models.CharField(
                choices=[("CONSUME", "CONSUME"), ("VALORIZE", "VALORIZE")],
                max_length=16,
                verbose_name="Type d'action",
            ),
        ),
    ]
