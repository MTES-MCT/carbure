import csv
import os


def load_matieres_premieres():
    """Load the shared feedstock catalog. Idempotent: keyed by code."""
    from core.models import MatierePremiere

    filename = "%s/web/fixtures/csv/matierespremieres.csv" % (os.environ["CARBURE_HOME"])

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, quotechar='"')
        for row in reader:
            code = row[0]
            if code == "code":
                continue

            name = row[1]
            compat_alcool = row[2]
            compat_graisse = row[3]
            is_double_compte = row[4]
            is_huile_vegetale = row[5]
            is_displayed = row[6]
            is_industrial_waste = row[7]
            category = row[8]
            MatierePremiere.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": "",
                    "compatible_alcool": compat_alcool,
                    "compatible_graisse": compat_graisse,
                    "is_double_compte": is_double_compte,
                    "is_huile_vegetale": is_huile_vegetale,
                    "is_displayed": is_displayed,
                    "is_industrial_waste": is_industrial_waste,
                    "category": category,
                    "is_biofuel_feedstock": True,
                },
            )


if __name__ == "__main__":
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
    django.setup()
    load_matieres_premieres()
