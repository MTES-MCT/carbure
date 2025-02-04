from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.models import Biocarburant, CarbureLot, GenericError, UserRights
from producers.models import ProductionSiteOutput
from transactions.models import ProductionSite


class SetBioFuelsSerializer(serializers.Serializer):
    biocarburant_codes = serializers.ListField(
        child=serializers.CharField(), required=True, help_text="List of biocarburant codes."
    )


class SetBioFuelsActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=SetBioFuelsSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=True, methods=["post"], url_path="set-biofuels")
    def set_biofuels(self, request, id=None):
        serializer = SetBioFuelsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bc_codes = serializer.validated_data["biocarburant_codes"]
        bc_list = Biocarburant.objects.filter(code__in=bc_codes)
        if not bc_list.exists():
            return Response(
                {"status": "error", "message": f"Unknown BC in list {bc_codes}"}, status=status.HTTP_400_BAD_REQUEST
            )
        ps = ProductionSite.objects.get(id=id)
        # we have all the data, make sure we are allowed to delete it

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if ps.producer not in rights:
            return Response(
                {"status": "forbidden", "message": f"User not allowed to edit production site {id}"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            ProductionSiteOutput.objects.filter(production_site=ps).delete()
            for bc in bc_list:
                _, created = ProductionSiteOutput.objects.update_or_create(production_site=ps, biocarburant=bc)
                if created:
                    # Remove errors and trigger background checks
                    impacted_txs = CarbureLot.objects.filter(carbure_production_site=ps, biofuel=bc)
                    background_bulk_scoring(impacted_txs)
                    background_bulk_sanity_checks(impacted_txs)
                    GenericError.objects.filter(lot__in=impacted_txs, error="BC_NOT_CONFIGURED").delete()

        except Exception:
            return Response(
                {"status": "error", "message": "Unknown error. Please contact an administrator"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "success"})
