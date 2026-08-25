from traceability.handlers.action import ActionIndustryLookups
from traceability.models import Material


class H2ActionLookups(ActionIndustryLookups):
    def material(self, _entity):
        return Material.objects.filter(code__startswith="H2-")
