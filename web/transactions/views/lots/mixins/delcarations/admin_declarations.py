import datetime
import math

from dateutil.relativedelta import relativedelta
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureLot, Entity, SustainabilityDeclaration
from core.serializers import SustainabilityDeclarationSerializer


class CountSerializer(serializers.Serializer):
    drafts = serializers.IntegerField()
    output = serializers.IntegerField()
    input = serializers.IntegerField()
    corrections = serializers.IntegerField()


class DeclarationSummarySerializer(serializers.Serializer):
    declaration = SustainabilityDeclarationSerializer()
    count = CountSerializer()


class DeclarationAdminMixin:
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
                "period",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Period",
                required=True,
            ),
        ],
        responses=DeclarationSummarySerializer,
    )
    @action(methods=["get"], detail=False, url_path="admin-declarations")
    def admin_declarations(self, request, *args, **kwargs):
        entity_id = request.query_params.get("entity_id")
        period = request.query_params.get("period", False)
        if not period:
            raise ValidationError({"message": "Missing period"})

        year = math.floor(int(period) / 100)
        month = int(period) % 100
        period_now_date = datetime.date(year=year, month=month, day=1)
        period_before_date = period_now_date - relativedelta(months=1)
        period_after_date = period_now_date + relativedelta(months=1)
        period_dates = [period_before_date, period_now_date, period_after_date]
        periods = [
            period_before_date.year * 100 + period_before_date.month,
            int(period),
            period_after_date.year * 100 + period_after_date.month,
        ]

        data = []
        lot_counts = get_period_entity_lot_count(periods)
        declaration_query = SustainabilityDeclaration.objects.filter(
            period__in=period_dates,
            entity__entity_type__in=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER],
        ).select_related("entity")
        declarations = SustainabilityDeclarationSerializer(declaration_query, many=True).data
        for decl in declarations:
            entity_id = decl.get("entity").get("id")
            period = decl.get("period")
            count = (
                lot_counts[entity_id][period]
                if entity_id in lot_counts and period in lot_counts[entity_id]
                else {"drafts": 0, "output": 0, "input": 0, "corrections": 0}
            )
            data.append({"declaration": decl, "count": count})
            return Response(data)


def get_period_entity_lot_count(periods):
    lots = CarbureLot.objects.filter(period__in=periods).values(
        "added_by_id",
        "carbure_supplier_id",
        "carbure_client_id",
        "lot_status",
        "correction_status",
        "period",
    )

    declarations = {}

    for lot in lots:
        period = lot["period"] or None
        author = lot["added_by_id"] or None
        vendor = lot["carbure_supplier_id"] or None
        client = lot["carbure_client_id"] or None

        if author and lot["lot_status"] == CarbureLot.DRAFT:
            declaration = init_declaration(author, period, declarations)
            declaration["drafts"] += 1
        else:
            if client:
                declaration = init_declaration(client, period, declarations)
                declaration["input"] += 1
            if vendor:
                declaration = init_declaration(vendor, period, declarations)
                declaration["output"] += 1
            if author and lot["correction_status"] != CarbureLot.NO_PROBLEMO:
                declaration = init_declaration(author, period, declarations)
                declaration["corrections"] += 1

    return declarations


def init_declaration(entity, period, declarations):
    if entity not in declarations:
        declarations[entity] = {}
    if period not in declarations[entity]:
        declarations[entity][period] = {
            "drafts": 0,
            "output": 0,
            "input": 0,
            "corrections": 0,
        }
    return declarations[entity][period]
