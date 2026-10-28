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
                    ("TEST1", "TEST1"),
                    ("TEST2", "TEST2"),
                    ("TEST3", "TEST3"),
                    ("VALORIZE", "VALORIZE"),
                ],
                max_length=16,
                verbose_name="Type d'action",
            ),
        ),
    ]
