from core.models import Pays


def setup_countries():
    Pays.objects.update_or_create(
        code_pays="FR",
        defaults={
            "name": "France",
            "name_en": "France",
            "is_in_europe": True,
        },
    )

    Pays.objects.update_or_create(
        code_pays="DE",
        defaults={
            "name": "Allemagne",
            "name_en": "Germany",
            "is_in_europe": True,
        },
    )

    Pays.objects.update_or_create(
        code_pays="US",
        defaults={
            "name": "États-Unis",
            "name_en": "United States",
            "is_in_europe": False,
        },
    )

    Pays.objects.update_or_create(
        code_pays="CN",
        defaults={
            "name": "Chine",
            "name_en": "China",
            "is_in_europe": False,
        },
    )


def get_country(code: str):
    return Pays.objects.get(code_pays=code)
