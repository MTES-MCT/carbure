from django.db.models.query_utils import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import CarbureLot, CarbureStockTransformation, Entity, UserRights
from saf.permissions import HasUserRights


class YearsSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


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
    responses=YearsSerializer,
    examples=[
        OpenApiExample(
            "Example of response.",
            value=[
                "2020",
                "2021",
                "2022",
                "2023",
                "2024",
            ],
            request_only=False,
            response_only=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes(
    [
        IsAuthenticated,
        HasUserRights(
            None,
            [
                Entity.OPERATOR,
                Entity.PRODUCER,
                Entity.TRADER,
                Entity.ADMIN,
                Entity.AUDITOR,
            ],
        ),
    ]
)
def get_years(request, *args, **kwargs):
    entity_id = request.query_params.get("entity_id")
    entity = Entity.objects.get(id=entity_id)
    lots_years = get_lots_years(request.user, entity)
    transforms_years = get_transforms_years(request.user, entity)

    years = list(set(list(lots_years) + list(transforms_years)))
    return Response(list(years))


def get_audited_entities(user):
    rights = UserRights.objects.filter(user=user, role=UserRights.AUDITOR)
    return rights.values_list("entity", flat=True)


def get_lots_years(user, entity):
    lots = CarbureLot.objects.exclude(lot_status=CarbureLot.DELETED)
    if entity.entity_type == Entity.AUDITOR:
        audited_entities = get_audited_entities(user)
        lots = lots.exclude(lot_status=CarbureLot.DRAFT).filter(
            Q(carbure_client__in=audited_entities)
            | Q(carbure_supplier__in=audited_entities)
            | Q(added_by__in=audited_entities)
        )
    elif entity.entity_type == Entity.ADMIN:
        lots = lots.exclude(lot_status=CarbureLot.DRAFT)

    else:
        lots = lots.exclude(Q(lot_status=CarbureLot.DRAFT) & ~Q(added_by_id=entity.id)).filter(
            Q(carbure_client_id=entity.id) | Q(carbure_supplier_id=entity.id) | Q(added_by_id=entity.id)
        )
        # only ignore drafts created by other entities

    lots = lots.values_list("year", flat=True).distinct()

    return lots


def get_transforms_years(user, entity):
    transforms_years = CarbureStockTransformation.objects.select_related("source_stock__parent_lot").exclude(
        source_stock__parent_lot__lot_status__in=[
            CarbureLot.DRAFT,
            CarbureLot.DELETED,
        ]
    )
    if entity.entity_type == Entity.AUDITOR:
        audited_entities = get_audited_entities(user)
        transforms_years = transforms_years.filter(entity_id__in=audited_entities)
    elif entity.entity_type == Entity.AUDITOR:
        transforms_years = transforms_years
    else:
        transforms_years = transforms_years.filter(entity_id=entity.id)

    transforms_years = transforms_years.values_list("transformation_dt__year", flat=True).distinct()

    return transforms_years
