import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("feedstocks", "0001_initial"),
        ("traceability", "0027_material_description_alter_material_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="classification",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="feedstocks.classification"
            ),
        ),
    ]
