from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0017_action_quantity_positive"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="actionstatus",
            index=models.Index(fields=["action", "-created_at", "-id"], name="action_status_latest"),
        ),
    ]
