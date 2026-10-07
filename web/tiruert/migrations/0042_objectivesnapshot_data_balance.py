from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tiruert", "0041_alter_operation_status_alter_operation_type_and_more")]

    operations = [
        migrations.AddField(
            model_name="objectivesnapshot",
            name="data_balance",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
