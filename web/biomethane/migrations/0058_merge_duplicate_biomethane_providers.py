from django.db import migrations

SUFFIX = " (fournisseur gaz)"
PROVIDER = "Fournisseur de biométhane"

# SIRENs stored by the fixture before biomethane_providers.csv was corrected.
LEGACY_SIRENS = {
    "947688099": "813273554",
    "814450151": "891588154",
    "915720015": "984306357",
    "491911400": "38 76 56 04 (CVR)",
    "824763536": "422716878",
    "530609668": "833755598",
    "314119504": "844431387",
    "428766976": "622037083",
    "493467591": "521913798",
    "442395448": "434582540",
}


def merge_duplicate_biomethane_providers(apps, schema_editor):
    """Correct legacy SIRENs, move contracts off duplicate providers, then delete those duplicates.

    A suffixed provider is kept when no unsuffixed provider shares its SIREN.
    """
    Entity = apps.get_model("core", "Entity")
    BiomethaneContract = apps.get_model("biomethane", "BiomethaneContract")

    for old_siren, new_siren in LEGACY_SIRENS.items():
        Entity.objects.filter(registration_id=old_siren, entity_type=PROVIDER).update(registration_id=new_siren)

    duplicates = Entity.objects.filter(entity_type=PROVIDER, name__endswith=SUFFIX)
    for duplicate in duplicates:
        canonical_name = duplicate.name[: -len(SUFFIX)]
        canonical = (
            Entity.objects.filter(
                entity_type=PROVIDER,
                registration_id=duplicate.registration_id,
                name=canonical_name,
            )
            .exclude(pk=duplicate.pk)
            .first()
        )
        if canonical is None:
            continue

        BiomethaneContract.objects.filter(buyer_id=duplicate.pk).update(buyer_id=canonical.pk)
        duplicate.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("biomethane", "0057_alter_biomethanefeedstocktariffcoefficient_collection_type_and_more"),
        ("core", "0088_alter_externaladminrights_right"),
    ]

    operations = [
        migrations.RunPython(merge_duplicate_biomethane_providers, migrations.RunPython.noop),
    ]
