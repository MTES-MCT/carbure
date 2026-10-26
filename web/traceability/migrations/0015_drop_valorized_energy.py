from django.db import migrations


def drop_valorized_energy(apps, schema_editor):
    Material = apps.get_model("traceability", "Material")
    Action = apps.get_model("traceability", "Action")

    try:
        material = Material.objects.get(code="VALORIZED-ENERGY")
    except Material.DoesNotExist:
        return

    for action in Action.objects.filter(material=material).select_related("parent"):
        action.material = None
        update_fields = ["material"]
        if action.parent_id is not None:
            action.quantity = action.parent.quantity
            update_fields.append("quantity")
        action.save(update_fields=update_fields)

    material.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0014_backfill_valorize_material"),
    ]

    operations = [
        migrations.RunPython(drop_valorized_energy, migrations.RunPython.noop),
    ]
