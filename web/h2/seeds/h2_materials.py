from traceability.models import Material


def setup_h2_materials():
    Material.objects.get_or_create(
        code="H2-RFBNO",
        defaults={"name": "Hydrogène RFNBO"},
    )

    Material.objects.get_or_create(
        code="H2-BIO",
        defaults={"name": "Bio-H2"},
    )


def get_rfnbo_hydrogen():
    return Material.objects.get(code="H2-RFBNO")


def get_bio_hydrogen():
    return Material.objects.get(code="H2-BIO")
