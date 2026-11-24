from django.db import migrations, models
from django.db.models import Count, Min


def remove_duplicate_tags(apps, schema_editor):
    MaterialTag = apps.get_model("traceability", "MaterialTag")
    tags = MaterialTag.objects.using(schema_editor.connection.alias)
    duplicates = (
        tags.values("material_id", "type", "value").annotate(first_id=Min("id"), total=Count("id")).filter(total__gt=1)
    )
    for duplicate in duplicates.iterator():
        tags.filter(material_id=duplicate["material_id"], type=duplicate["type"], value=duplicate["value"]).exclude(
            pk=duplicate["first_id"]
        ).delete()


class Migration(migrations.Migration):
    dependencies = [("traceability", "0028_material_classification")]

    operations = [
        migrations.RunPython(remove_duplicate_tags, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="materialtag",
            constraint=models.UniqueConstraint(fields=("material", "type", "value"), name="material_tag_unique"),
        ),
    ]
