from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core import private_storage
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

        if agreement.application:
            if entity.entity_type in [Entity.ADMIN, Entity.PRODUCER, Entity.EXTERNAL_ADMIN]:
                result["application"]["download_link"] = (
                    private_storage.url(agreement.application.download_link) if agreement.application.download_link else None
                )
            else:
                result["application"]["download_link"] = None

        if entity.entity_type in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]:
            result["has_dechets_industriels"] = False
            if agreement.application:
                result["has_dechets_industriels"] = check_has_dechets_industriels(agreement.application)

        return Response(result)
