from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0026_materialtag_material_tag_values_per_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="description",
            field=models.CharField(blank=True, default="", max_length=512),
        ),
        migrations.AlterField(
            model_name="material",
            name="name",
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
