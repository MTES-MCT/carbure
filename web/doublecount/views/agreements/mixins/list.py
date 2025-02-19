from datetime import datetime

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from certificates.models import DoubleCountingRegistration
from core.models import Entity
from doublecount.helpers import get_quotas
from doublecount.models import DoubleCountingApplication
from doublecount.serializers import DoubleCountingApplicationPartialSerializer


class ListActionMixin(ListModelMixin):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(
                "year",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Year",
                required=False,
            ),
        ],
        responses=DoubleCountingApplicationPartialSerializer,
    )
    def list(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        company_id = self.request.query_params.get("company_id")
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type == Entity.ADMIN:
            entity_id = company_id

        producer_applications = DoubleCountingApplication.objects.filter(producer_id=entity_id)
        if len(producer_applications) == 0:
            return Response([])

        applications_data = DoubleCountingApplicationPartialSerializer(producer_applications, many=True).data
        current_year = datetime.now().year
        quotas = get_quotas(year=current_year, producer_id=entity_id)

        # add quotas to active agreements
        for application in applications_data:
            if application["status"] != DoubleCountingApplication.ACCEPTED:
                application["quotas_progression"] = None
                continue
            found_quotas = [q for q in quotas if q["certificate_id"] == application["certificate_id"]]
            application["quotas_progression"] = (
                round(found_quotas[0]["quotas_progression"], 2) if len(found_quotas) > 0 else 0
            )

            # add agreement_id to applications when accepted
            try:
                agreement = DoubleCountingRegistration.objects.get(application_id=application["id"])
                application["agreement_id"] = agreement.id
            except Exception:
                application["agreement_id"] = None

        return Response(applications_data)
