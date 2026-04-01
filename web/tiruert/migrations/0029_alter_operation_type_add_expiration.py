from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tiruert", "0028_objectivesnapshot"),
    ]

    operations = [
        migrations.AlterField(
            model_name="operation",
            name="type",
            field=models.CharField(
                choices=[
                    ("INCORPORATION", "INCORPORATION"),
                    ("CESSION", "CESSION"),
                    ("TENEUR", "TENEUR"),
                    ("LIVRAISON_DIRECTE", "LIVRAISON_DIRECTE"),
                    ("MAC_BIO", "MAC_BIO"),
                    ("EXPORTATION", "EXPORTATION"),
                    ("EXPEDITION", "EXPEDITION"),
                    ("DEVALUATION", "DEVALUATION"),
                    ("CUSTOMS_CORRECTION", "CUSTOMS_CORRECTION"),
                    ("TRANSFERT", "TRANSFERT"),
                    ("EXPIRATION", "EXPIRATION"),
                ],
                max_length=20,
            ),
        ),
    ]
