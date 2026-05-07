from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0072_elecprovisioncertificate_enr_ratio"),
    ]

    operations = [
        migrations.AddField(
            model_name="eleccertificatereadjustment",
            name="provision_certificate",
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, to="elec.elecprovisioncertificate"),
        ),
    ]
