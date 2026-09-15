from django.db import migrations, models


def rename_heating_usage(apps, schema_editor):
    CarbureLot = apps.get_model("core", "CarbureLot")
    CarbureLot.objects.filter(usage="HEATING").update(usage="COMBUSTIBLE")


def restore_heating_usage(apps, schema_editor):
    CarbureLot = apps.get_model("core", "CarbureLot")
    CarbureLot.objects.filter(usage="COMBUSTIBLE").update(usage="HEATING")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0080_merge_20260824_1747"),
    ]

    operations = [
        migrations.RunPython(rename_heating_usage, restore_heating_usage),
        migrations.AlterField(
            model_name="carburelot",
            name="usage",
            field=models.CharField(
                blank=True,
                choices=[
                    ("ROAD", "ROAD"),
                    ("COMBUSTIBLE", "COMBUSTIBLE"),
                    ("AGRICULTURE", "AGRICULTURE"),
                    ("CONSTRUCTION", "CONSTRUCTION"),
                    ("MARITIME", "MARITIME"),
                    ("INLAND_WATERWAY", "INLAND_WATERWAY"),
                    ("RAIL", "RAIL"),
                    ("FISHING", "FISHING"),
                    ("OTHER", "OTHER"),
                ],
                default="",
                max_length=64,
            ),
        ),
    ]
