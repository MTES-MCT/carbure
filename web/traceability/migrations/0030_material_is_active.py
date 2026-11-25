from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0026_alter_action_type"),
        ("traceability", "0029_materialtag_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Active"),
        ),
    ]
