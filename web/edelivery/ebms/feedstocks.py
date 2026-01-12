from core.models import MatierePremiere


def from_UDB_feedstock_code(_):
    return MatierePremiere.objects.get(code="BETTERAVE")
