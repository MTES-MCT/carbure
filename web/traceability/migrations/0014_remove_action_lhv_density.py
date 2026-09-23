from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0011_action_file"),
        ("traceability", "0013_action_lhv_density"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="action",
            name="action_lhv_null_or_positive",
        ),
        migrations.RemoveConstraint(
            model_name="action",
            name="action_density_null_or_positive",
        ),
        migrations.RemoveField(
            model_name="action",
            name="density",
        ),
        migrations.RemoveField(
            model_name="action",
            name="lhv",
        ),
    ]
