from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apikey.authentication import APIKeyAuthentication
from core.helpers import get_lot_comments, get_lot_updates, get_stock_events
from core.models import (
    CarbureLot,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    UserRights,
)
from core.serializers import (
    CarbureLotCommentSerializer,
    CarbureLotEventSerializer,
    CarbureLotPublicSerializer,
    CarbureStockPublicSerializer,
    CarbureStockTransformationPublicSerializer,
)
from transactions.filters import StockFilter
from transactions.permissions import HasUserRights

from .mixins import ActionMixins


class StockDetailsResponseSerializer(serializers.Serializer):
    stock = CarbureStockPublicSerializer()
    parent_lot = CarbureLotPublicSerializer(allow_null=True)
    parent_transformation = CarbureStockTransformationPublicSerializer(allow_null=True)
    children_lot = CarbureLotPublicSerializer(many=True)
    children_transformation = CarbureStockTransformationPublicSerializer(many=True)
    events = CarbureLotCommentSerializer(many=True)
    updates = CarbureLotCommentSerializer(many=True)
    comments = CarbureLotEventSerializer(many=True)


class StockViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, ActionMixins):
    lookup_field = "id"
    serializer_class = CarbureStockPublicSerializer
    filterset_class = StockFilter
    permission_classes = (
        IsAuthenticated,
        HasUserRights(
            None,
            [
                Entity.AUDITOR,
                Entity.ADMIN,
                Entity.OPERATOR,
                Entity.PRODUCER,
                Entity.TRADER,
                Entity.POWER_OR_HEAT_PRODUCER,
            ],
        ),
    )
    ordering_fields = ["id", "remaining_volume", "biofuel", "supplier", "country"]
    search_fields = [
        "feedstock__name",
        "biofuel__name",
        "carbure_id",
        "country_of_origin__name",
        "depot__name",
        "parent_lot__free_field",
        "parent_lot__transport_document_reference",
    ]

    def get_authenticators(self):
        if self.request:
            method = self.request.method.lower()

            if method == "options":
                self.action = "metadata"
            else:
                self.action = self.action_map.get(method)
            if self.action in ["list", "extract_lots", "split"]:
                return [
                    SessionAuthentication(),
                    BasicAuthentication(),
                    APIKeyAuthentication(),
                ]
        return super().get_authenticators()

    def get_permissions(self):
        if self.action in ["cancel_transformation", "flush", "split", "transform"]:
            return [
                HasUserRights(
                    [UserRights.ADMIN, UserRights.RW],
                    [
                        Entity.OPERATOR,
                        Entity.PRODUCER,
                        Entity.TRADER,
                        Entity.POWER_OR_HEAT_PRODUCER,
                    ],
                ),
            ]
        return super().get_permissions()

    def get_queryset(self):
        queryset = CarbureStock.objects.none()
        if getattr(self, "swagger_fake_view", False):
            return queryset
        if self.request and not self.request.user.is_anonymous:
            entity_id = self.request.query_params.get("entity_id")
            entity = Entity.objects.get(id=entity_id)

            if entity.entity_type == Entity.ADMIN:
                queryset = CarbureStock.objects.all()
            elif entity.entity_type == Entity.AUDITOR:
                rights = UserRights.objects.filter(user=entity_id, role=UserRights.AUDITOR)
                entities = [r.entity_id for r in rights]
                queryset = CarbureStock.objects.filter(carbure_client__in=entities)
            else:
                queryset = CarbureStock.objects.filter(carbure_client_id=entity_id)

            queryset = queryset.select_related(
                "parent_lot",
                "parent_transformation",
                "biofuel",
                "feedstock",
                "country_of_origin",
                "depot",
                "depot__country",
                "carbure_production_site",
                "carbure_production_site__country",
                "production_country",
                "carbure_client",
                "carbure_supplier",
            )

            history = self.request.query_params.get("history", False)
            if history != "true":
                queryset = queryset.filter(remaining_volume__gt=0)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
        responses=StockDetailsResponseSerializer,
    )
    def retrieve(self, request, id=None):
        entity_id = request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)
        stock = self.get_object()

        data = {}
        data["stock"] = CarbureStockPublicSerializer(stock).data
        data["parent_lot"] = CarbureLotPublicSerializer(stock.parent_lot).data if stock.parent_lot else None
        data["parent_transformation"] = (
            CarbureStockTransformationPublicSerializer(stock.parent_transformation).data
            if stock.parent_transformation
            else None
        )
        children = CarbureLot.objects.filter(parent_stock=stock).exclude(lot_status=CarbureLot.DELETED)
        data["children_lot"] = CarbureLotPublicSerializer(children, many=True).data
        data["children_transformation"] = CarbureStockTransformationPublicSerializer(
            CarbureStockTransformation.objects.filter(source_stock=stock), many=True
        ).data
        data["events"] = get_stock_events(stock.parent_lot)
        data["updates"] = get_lot_updates(stock.parent_lot, entity)
        data["comments"] = get_lot_comments(stock.parent_lot)

        return Response(data)
