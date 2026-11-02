from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0089_remove_legacy_ml_errors"),
    ]

    operations = [
        migrations.RemoveField(model_name="carburelot", name="ml_control_requested"),
        migrations.RemoveField(model_name="carburelot", name="ml_scoring"),
    ]
