from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("certificates", "0008_alter_doublecountingregistration_production_site_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="doublecountingregistration",
            name="status",
            field=models.CharField(
                choices=[
                    ("VALID", "Valide"),
                    ("SUSPENDED", "Suspendu"),
                    ("WITHDRAWN", "Retiré"),
                    ("TERMINATED", "Interrompu"),
                ],
                default="VALID",
                max_length=16,
            ),
        ),
    ]
