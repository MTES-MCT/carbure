from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0018_actionstatus_action_status_latest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="action",
            name="type",
            field=models.CharField(
                choices=[("INIT", "INIT"), ("VALORIZE", "VALORIZE"), ("TRANSFER", "TRANSFER")],
                max_length=16,
                verbose_name="Type d'action",
            ),
        ),
    ]
