from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from elec.models import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSerializer


class ElecChargePointViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ElecChargePointSerializer
    queryset = ElecChargePoint.objects.all()
