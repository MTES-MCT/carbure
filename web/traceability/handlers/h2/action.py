from h2.permissions import HasHRSRights, HasHRSWriteRights
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.h2.lookups import H2ActionLookups
from traceability.models import Action


class H2ActionHandler(ActionIndustryHandler):
    industry = Action.H2
    lookups_class = H2ActionLookups
    excel_column_labels = {
        "quantity": "Quantité (MJ)",
        "material": "Nature d'hydrogène",
    }

    @staticmethod
    def get_permissions(action: str):
        if action in ["create", "update", "partial_update", "destroy"]:
            return [HasHRSWriteRights()]
        return [HasHRSRights()]
