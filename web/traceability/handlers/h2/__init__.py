from h2.permissions import HasHRSRights, HasHRSWriteRights
from traceability.handlers.action import ActionIndustryHandler
from traceability.models import Action


class H2ActionHandler(ActionIndustryHandler):
    industry = Action.H2

    @staticmethod
    def get_permissions(action: str):
        if action in ["create", "update", "partial_update", "destroy"]:
            return [HasHRSWriteRights()]
        return [HasHRSRights()]
