import traceback

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.helpers import get_lots_summary_data
from core.models import Entity
from transactions.views.helpers import get_admin_summary_data


class LotsInOutSerializer(serializers.Serializer):
    supplier = serializers.CharField()
    client = serializers.CharField(required=False)
    biofuel_code = serializers.CharField()
    delivery_type = serializers.CharField(required=False)
    volume_sum = serializers.FloatField()
    weight_sum = serializers.FloatField()
    lhv_amount_sum = serializers.FloatField()
    avg_ghg_reduction = serializers.FloatField()
    total = serializers.IntegerField()
    pending = serializers.IntegerField()


class SummaryResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total_volume = serializers.FloatField()
    total_weight = serializers.FloatField()
    total_lhv_amount = serializers.FloatField()
    in_ = serializers.ListField(child=LotsInOutSerializer(), source="in")
    out = serializers.ListField(child=LotsInOutSerializer())
    lots = serializers.ListField(child=LotsInOutSerializer())


class SummaryMixin:
    @extend_schema(
        filters=True,
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        responses=SummaryResponseSerializer,
    )
    @action(methods=["get"], detail=False)
    def summary(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        short = self.request.query_params.get("short", False)
        query_status = self.request.query_params.get("status", False)

        entity = get_object_or_404(Entity, id=entity_id)

        mutable_params = request.GET.copy()
        mutable_params["will_aggregate"] = "true"
        request.GET = mutable_params

        lots = self.filter_queryset(self.get_queryset())

        if not query_status:
            raise ValidationError({"message": "Missing status"})
        try:
            entity = Entity.objects.get(id=entity_id)
            if entity.entity_type in [Entity.AUDITOR, Entity.ADMIN]:
                summary = get_admin_summary_data(lots, short == "true")
            else:
                summary = get_lots_summary_data(lots, entity, short == "true")
            return Response(summary)

        except Exception:
            traceback.print_exc()
            return Response(
                {"status": "error", "message": "Could not get lots summary"},
                status=status.HTTP_400_BAD_REQUEST,
            )
