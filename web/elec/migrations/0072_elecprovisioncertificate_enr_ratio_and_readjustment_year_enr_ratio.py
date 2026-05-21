from django.db import migrations, models


def backfill_readjustment_year_and_enr_ratio(apps, schema_editor):
    readjustment_model = apps.get_model("elec", "ElecCertificateReadjustment")
    readjustment_model.objects.filter(year__isnull=True).update(year=2025)
    readjustment_model.objects.filter(enr_ratio__isnull=True).update(enr_ratio=0.25)


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0071_elecprovisioncertificate_date_from_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="elecprovisioncertificate",
            name="enr_ratio",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="eleccertificatereadjustment",
            name="year",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="eleccertificatereadjustment",
            name="enr_ratio",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_readjustment_year_and_enr_ratio, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="eleccertificatereadjustment",
            name="year",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="eleccertificatereadjustment",
            name="enr_ratio",
            field=models.FloatField(),
        ),
    ]
