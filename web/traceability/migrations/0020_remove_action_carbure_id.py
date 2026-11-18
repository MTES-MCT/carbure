from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0019_action_carbure_id_optional_pos"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="action",
            name="carbure_id",
        ),
    ]
