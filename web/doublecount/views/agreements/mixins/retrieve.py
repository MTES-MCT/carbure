from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.models import Entity
from doublecount.helpers import get_agreement_quotas
from doublecount.views.applications.mixins.utils import check_has_dechets_industriels


class AgreementRetrieveActionMixin(RetrieveModelMixin):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        responses=DoubleCountingRegistrationDetailsSerializer,
    )
    def retrieve(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)

        agreement = self.get_object()
        result = DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data
        result["quotas"] = get_agreement_quotas(agreement)

        if entity.entity_type == Entity.ADMIN:
            result["has_dechets_industriels"] = False
            if agreement.application:
                result["has_dechets_industriels"] = check_has_dechets_industriels(agreement.application)

        return Response(result)
