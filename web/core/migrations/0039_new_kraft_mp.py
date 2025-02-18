from django.db import migrations


def create_new_mp(apps, schema_editor):
    matiere_premiere = apps.get_model("core", "MatierePremiere")
    matiere_premiere.objects.create(
        name="Méthanol brut issu de la pâte kraft obtenue à partir de la pulpe de bois",
        name_en="Raw methanol from kraft pulping stemming from the production of wood pulp",
        description="",
        code="RAW_METHANOL_KRAFT_PULPING",
        compatible_alcool=False,
        compatible_graisse=False,
        is_double_compte=True,
        is_huile_vegetale=False,
        is_displayed=True,
        category="ANN-IX-A",
        dgddi_category=None,
    )


def delete_new_mp(apps, schema_editor):
    matiere_premiere = apps.get_model("core", "MatierePremiere")
    matiere_premiere.objects.filter(code="RAW_METHANOL_KRAFT_PULPING").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0038_alter_matierepremiere_category"),
    ]
    operations = [
        migrations.RunPython(create_new_mp, reverse_code=delete_new_mp),
    ]
