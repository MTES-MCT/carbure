from django.db.models.query_utils import Q
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    PolymorphicProxySerializer,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.helpers import get_auditor_stock
from core.models import CarbureLot, CarbureStock, Entity
from saf.permissions import HasUserRights
from transactions.views.utils import get_auditor_lots


class SnapshotReponseSerializer(serializers.Serializer):
    draft = serializers.IntegerField()
    in_total = serializers.IntegerField()
    in_pending = serializers.IntegerField()
    in_tofix = serializers.IntegerField()
    stock = serializers.IntegerField()
    stock_total = serializers.IntegerField()
    out_total = serializers.IntegerField()
    out_pending = serializers.IntegerField()
    out_tofix = serializers.IntegerField()
    draft_imported = serializers.IntegerField()
    draft_stocks = serializers.IntegerField()


class AdminSnapshotReponseSerializer(serializers.Serializer):
    alerts = serializers.IntegerField()
    lots = serializers.IntegerField()
    stocks = serializers.IntegerField()


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
    responses={
        200: OpenApiResponse(
            description="Response regular user or admin or auditor user",
            response=PolymorphicProxySerializer(
                component_name="Response200",
                serializers=[SnapshotReponseSerializer, AdminSnapshotReponseSerializer],
                resource_type_field_name=None,
            ),
        )
    },
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
                Entity.AUDITOR,
                Entity.ADMIN,
            ],
        ),
    ]
)
def get_snapshot(request, *args, **kwargs):
    entity_id = request.query_params.get("entity_id")
    entity = Entity.objects.get(id=entity_id)
    year = request.query_params.get("year")
    if not year:
        raise ValidationError({"message": "Missing year"})

    try:
        year = int(year)
    except Exception:
        return Response(
            {"message": "Incorrect format for year. Expected YYYY"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if entity.entity_type in Entity.ADMIN:
        lots = CarbureLot.objects.filter(year=year).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        stock = CarbureStock.objects.filter(remaining_volume__gt=0)
        alerts = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
            Q(highlighted_by_admin=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
        )
    if entity.entity_type == Entity.AUDITOR:
        auditor_lots = get_auditor_lots(request).filter(year=year)
        lots = auditor_lots.filter(year=year).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
        alerts = lots.exclude(audit_status=CarbureLot.CONFORM).filter(
            Q(highlighted_by_auditor=True) | Q(random_control_requested=True) | Q(ml_control_requested=True)
        )

        auditor_stock = get_auditor_stock(request.user)
        stock = auditor_stock.filter(remaining_volume__gt=0)

    if entity.entity_type in [Entity.AUDITOR, Entity.ADMIN]:
        data = {}
        data["lots"] = {
            "alerts": alerts.count(),
            "lots": lots.count(),
            "stocks": stock.count(),
        }
        return Response(data)

    lots = CarbureLot.objects.filter(year=year)

    drafts = lots.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
    drafts_imported = drafts.exclude(parent_stock__isnull=False)
    drafts_stocks = drafts.filter(parent_stock__isnull=False)

    lots_in = lots.filter(carbure_client_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_in_pending = lots_in.filter(lot_status=CarbureLot.PENDING)
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    stock = CarbureStock.objects.filter(carbure_client_id=entity_id)
    stock_not_empty = stock.filter(remaining_volume__gt=0)

    lots_out = lots.filter(carbure_supplier_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    data = {
        "draft": drafts.count(),
        "in_total": lots_in.count(),
        "in_pending": lots_in_pending.count(),
        "in_tofix": lots_in_tofix.count(),
        "stock": stock_not_empty.count(),
        "stock_total": stock.count(),
        "out_total": lots_out.count(),
        "out_pending": lots_out_pending.count(),
        "out_tofix": lots_out_tofix.count(),
        "draft_imported": drafts_imported.count(),
        "draft_stocks": drafts_stocks.count(),
    }
    return Response(data)
