import h2.handlers.lookups as lookups
from h2.permissions import HasHRSRights, HasHRSWriteRights
from h2.serializers.action import H2ActionExcelImportSerializer
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.excel import EXCEL_PRODUCTION_COLOR, EXCEL_TRANSPORT_COLOR, excel_column
from traceability.models import Action


class H2ActionHandler(ActionIndustryHandler):
    industry = Action.H2
    lookups = lookups
    excel_import_serializer_class = H2ActionExcelImportSerializer
    excel_columns = [
        {
            "key": "lot_id",
            "header": "ID_LOT/Batch ID",
            "comment": "Peut être répété sur plusieurs lignes si le lot est fractionné entre plusieurs stations / mois",
            "color": EXCEL_PRODUCTION_COLOR,
        },
        excel_column("pos_id", header="N° de PoS"),
        {
            "key": "lot_quantity",
            "header": "Quantite (kg)",
            "comment": "Quantité TOTALE du lot, constante quelle que soit la ligne (ne pas re-décompter)",
            "color": EXCEL_PRODUCTION_COLOR,
        },
        {
            "key": "producer",
            "header": "Producteur",
            "comment": "Raison sociale du producteur",
            "color": EXCEL_PRODUCTION_COLOR,
        },
        excel_column("certificate", header="N° du certificat du producteur"),
        excel_column("material", header="Nature d'H2"),
        excel_column("ei"),
        excel_column("ep"),
        {
            "header": "L'H2 est-il consommé sur le site de production",
            "comment": "Si oui, passer directement à la section consommation — Oui/Non",
            "color": EXCEL_TRANSPORT_COLOR,
        },
        excel_column("shipping_method"),
        excel_column("shipping_distance"),
        {"header": "Masse transportée (kg)", "color": EXCEL_TRANSPORT_COLOR},
        {"header": "Type de carburant pour le transport", "color": EXCEL_TRANSPORT_COLOR},
        excel_column("shipping_date"),
        excel_column("etd"),
        excel_column("site", header="Station", comment="Liste de choix - Nom de la station dans carbure"),
        excel_column("quantity", header="Quantité consommée (MJ)"),
        excel_column("eu"),
        excel_column("eccs"),
        excel_column("working_date"),
    ]

    @classmethod
    def get_permissions(cls, action: str):
        if action in cls.write_actions:
            return [HasHRSWriteRights()]
        return [HasHRSRights()]
