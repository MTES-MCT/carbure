from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from elec.filters import ElecChargePointApplicationFilter
from elec.models import ElecChargePointApplication
from elec.serializers.elec_charge_point_application import (
    ElecChargePointApplicationDetailsSerializer,
    ElecChargePointApplicationSerializer,
)

from .mixins import ActionMixin


class ElecChargePointApplicationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    serializer_class = ElecChargePointApplicationSerializer
    queryset = ElecChargePointApplication.objects.all()
    filterset_class = ElecChargePointApplicationFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ElecChargePointApplicationDetailsSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        company_id = self.request.query_params.get("company_id", None)
        if company_id:
            entity = Entity.objects.filter(entity_type=Entity.CPO, id=company_id)
            if not entity:
                raise ValidationError({"message": "MALFORMED_PARAMS"})

        return ElecChargePointApplication.objects.get_annotated_applications().filter(audit_sample__isnull=False)
