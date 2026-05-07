from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from tiruert.filters import MacFilter
from tiruert.models import MacFossilFuel
from tiruert.permissions import HasTiruertRightsObjectives, HasTiruertWriteRights
from tiruert.serializers import MacFossilFuelSerializer

from .mixins import ExcelExportActionMixin, ReplaceActionMixin


class MacFossilFuelViewSet(ExcelExportActionMixin, ReplaceActionMixin, ListModelMixin, GenericViewSet):
    queryset = MacFossilFuel.objects.all().order_by("year", "period", "fuel__nomenclature", "id")
    filterset_class = MacFilter
    serializer_class = MacFossilFuelSerializer
    permission_classes = [HasTiruertRightsObjectives]

    def get_permissions(self):
        if self.action == "replace":
            return [HasTiruertWriteRights()]
        return super().get_permissions()


MacFossilFuelExportViewSet = MacFossilFuelViewSet
