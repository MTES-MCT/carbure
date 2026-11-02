from django.db import migrations


def assign_valorized_energy(apps, schema_editor):
    Material = apps.get_model("traceability", "Material")
    Action = apps.get_model("traceability", "Action")
    material, _created = Material.objects.get_or_create(
        code="VALORIZED-ENERGY",
        defaults={"name": "VALORIZED_ENERGY", "unit": "MJ"},
    )
    Action.objects.filter(type="VALORIZE").update(material=material)


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0013_material_code_max_length"),
    ]

    operations = [
        migrations.RunPython(assign_valorized_energy, migrations.RunPython.noop),
    ]
