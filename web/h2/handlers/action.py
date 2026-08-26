import h2.handlers.lookups as lookups
from h2.permissions import HasHRSRights, HasHRSWriteRights
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.excel import excel_column
from traceability.models import Action


class H2ActionHandler(ActionIndustryHandler):
    industry = Action.H2
    lookups = lookups
    excel_columns = [
        excel_column("pos_id"),
        excel_column("material", header="Nature d'hydrogène"),
        excel_column("quantity", header="Quantité (MJ)"),
        excel_column("site", header="Station"),
        excel_column("shipping_date"),
        excel_column("shipping_distance"),
        excel_column("shipping_method"),
        excel_column("ei"),
        excel_column("ep"),
        excel_column("etd"),
        excel_column("eu"),
        excel_column("eccs"),
    ]

    @staticmethod
    def get_permissions(action: str):
        if action in ActionIndustryHandler.write_actions:
            return [HasHRSWriteRights()]
        return [HasHRSRights()]
