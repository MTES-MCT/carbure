from core.models import Biocarburant, MatierePremiere


def from_UDB_biofuel_code(_):
    return Biocarburant.objects.get(code="BG")


def from_UDB_feedstock_code(_):
    return MatierePremiere.objects.get(code="BETTERAVE")
