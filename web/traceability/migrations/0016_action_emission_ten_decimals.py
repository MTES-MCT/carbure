from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0015_action_emission_nine_decimals"),
    ]

    operations = [
        migrations.AlterField(
            model_name="action",
            name=name,
            field=models.DecimalField(decimal_places=10, default=Decimal("0"), max_digits=13),
        )
        for name in ("eec", "el", "ei", "ep", "etd", "eu", "eccs", "esca", "eccr")
    ]
