from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0025_rename_action_type_init_to_consume"),
    ]

    operations = [
        migrations.AlterField(
            model_name="action",
            name="type",
            field=models.CharField(
                choices=[("CONSUME", "CONSUME"), ("VALORIZE", "VALORIZE"), ("TRANSFER", "TRANSFER")],
                max_length=16,
                verbose_name="Type d'action",
            ),
        ),
    ]
