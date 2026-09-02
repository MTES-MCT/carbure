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
            "header": "Id du lot",
            "comment": "Identifiant dans votre système",
            "color": EXCEL_PRODUCTION_COLOR,
        },
        excel_column("certificate"),
        {"header": "N° de batch (batch ID)", "color": EXCEL_PRODUCTION_COLOR},
        excel_column("material", header="Nature d'hydrogène"),
        excel_column("pos_id"),
        excel_column("ei"),
        excel_column("ep"),
        {"header": "Consommation sur le site de production", "color": EXCEL_TRANSPORT_COLOR, "comment": "Oui/Non"},
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
    ]

    @staticmethod
    def get_permissions(action: str):
        if action in ActionIndustryHandler.write_actions:
            return [HasHRSWriteRights()]
        return [HasHRSRights()]
