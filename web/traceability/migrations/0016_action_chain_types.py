from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0015_drop_valorized_energy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="action",
            name="type",
            field=models.CharField(
                choices=[
                    ("INIT", "INIT"),
                    ("PRODUCE", "PRODUCE"),
                    ("MOVE", "MOVE"),
                    ("CONSUME", "CONSUME"),
                    ("VALORIZE", "VALORIZE"),
                ],
                max_length=16,
                verbose_name="Type d'action",
            ),
        ),
    ]
