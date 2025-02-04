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
from core.models import CarbureLot, GenericError, MatierePremiere, UserRights
from producers.models import ProductionSiteInput
from transactions.models import ProductionSite


class SetFeedstocksSerializer(serializers.Serializer):
    matiere_premiere_codes = serializers.ListField(child=serializers.CharField(), required=True)


class SetFeedstocksActionMixin:
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
        request=SetFeedstocksSerializer,
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
    @action(detail=True, methods=["post"], url_path="set-feedstocks")
    def set_feedstocks(self, request, id=None):
        serializer = SetFeedstocksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mp_codes = serializer.validated_data["matiere_premiere_codes"]

        ps = ProductionSite.objects.get(id=id)
        mp_list = MatierePremiere.objects.filter(code__in=mp_codes)
        if not mp_list.exists():
            return Response(
                {"message": "Unknown MP in list %s" % (mp_list)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if ps.producer not in rights:
            return Response(
                {
                    "message": "User not allowed to edit production site %s" % (id),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ProductionSiteInput.objects.filter(production_site=ps).delete()
            for mp in mp_list:
                obj, created = ProductionSiteInput.objects.update_or_create(production_site=ps, matiere_premiere=mp)
                if created:
                    # Remove errors and trigger background checks
                    impacted_txs = CarbureLot.objects.filter(carbure_production_site=ps, feedstock=mp)
                    background_bulk_scoring(impacted_txs)
                    background_bulk_sanity_checks(impacted_txs)
                    GenericError.objects.filter(lot__in=impacted_txs, error="MP_NOT_CONFIGURED").delete()

        except Exception:
            return Response(
                {
                    "message": "Unknown error. Please contact an administrator",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "success"})
