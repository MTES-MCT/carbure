from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("biomethane", "0048_remove_biomethanesupplyinput_source_and_crop_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="biomethanesupplyinput",
            name="material_unit",
            field=models.CharField(
                blank=True,
                choices=[("DRY", "Sèche"), ("WET", "Brute")],
                max_length=5,
                null=True,
            ),
        ),
    ]
