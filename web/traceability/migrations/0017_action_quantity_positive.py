from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0016_action_action_industry_type_date"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="action",
            constraint=models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="action_quantity_positive",
            ),
        ),
    ]
