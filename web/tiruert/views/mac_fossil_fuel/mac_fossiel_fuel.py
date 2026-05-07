from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from tiruert.filters import MacFilter
from tiruert.models import MacFossilFuel
from tiruert.permissions import HasTiruertRightsObjectives
from tiruert.serializers import MacFossilFuelSerializer

from .mixins import ExcelExportActionMixin


class MacFossilFuelViewSet(ExcelExportActionMixin, ListModelMixin, GenericViewSet):
    queryset = MacFossilFuel.objects.all().order_by("year", "period", "fuel__nomenclature", "id")
    filterset_class = MacFilter
    serializer_class = MacFossilFuelSerializer
    permission_classes = [HasTiruertRightsObjectives]


MacFossilFuelExportViewSet = MacFossilFuelViewSet
