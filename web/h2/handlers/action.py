import h2.handlers.lookups as lookups
from h2.permissions import HasHRSRights, HasHRSWriteRights
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.excel import excel_column
from traceability.models import Action


class H2ActionHandler(ActionIndustryHandler):
    industry = Action.H2
    lookups = lookups
    excel_columns = [
        excel_column("pos_id", color="#D9EAF7"),
        excel_column("material", header="Nature d'hydrogène", color="#D9EAF7"),
        excel_column("quantity", header="Quantité (MJ)", color="#D9EAF7"),
        excel_column("ei", color="#D9EAF7"),
        excel_column("ep", color="#D9EAF7"),
        excel_column("shipping_date", color="#FCE4D6"),
        excel_column("shipping_distance", color="#FCE4D6"),
        excel_column("shipping_method", color="#FCE4D6"),
        excel_column("etd", color="#FCE4D6"),
        excel_column("site", header="Station", color="#E2F0D9", comment="Liste de choix - Nom de la station dans carbure"),
        excel_column("eu", color="#E2F0D9"),
        excel_column("eccs", color="#E2F0D9"),
    ]

    @staticmethod
    def get_permissions(action: str):
        if action in ActionIndustryHandler.write_actions:
            return [HasHRSWriteRights()]
        return [HasHRSRights()]
