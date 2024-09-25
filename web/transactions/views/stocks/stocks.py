from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.helpers import get_lot_comments, get_lot_updates, get_stock_events
from core.models import CarbureLot, CarbureStock, CarbureStockTransformation, Entity
from core.serializers import (
    CarbureLotPublicSerializer,
    CarbureStockPublicSerializer,
    CarbureStockTransformationPublicSerializer,
)
from transactions.filters import StockFilter

from .mixins import ActionMixins


class StockViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, ActionMixins):
    lookup_field = "id"
    serializer_class = CarbureStockPublicSerializer
    filterset_class = StockFilter
    ordering_fields = ["id", "remaining_volume", "biofuel", "supplier", "country"]

    def get_queryset(self):
        entity_id = self.request.query_params.get("entity_id")
        queryset = CarbureStock.objects.filter(carbure_client_id=entity_id).select_related(
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

    def retrieve(self, request, id=None):
        entity_id = request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)
        stock = self.get_object()
        if stock.carbure_client_id != entity.id:
            raise PermissionDenied({"message": "User not allowed"})

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

    # def list(self, request, *args, **kwargs):
    #     export = query.get("export", False)

    #     entity_id = self.request.query_params.get("entity_id")
    #     query = self.request.query_params
    #     stock = self.filter_queryset(self.get_queryset())

    #     # enrich dataset with additional metadata
    #     serializer = CarbureStockPublicSerializer(stock, many=True)

    #     return Response(serializer.data)
    # else:
    #     file_location = export_carbure_stock(returned)
    #     with open(file_location, "rb") as excel:
    #         data = excel.read()
    #         ctype = (
    #             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         )
    #         response = HttpResponse(content=data, content_type=ctype)
    #         response["Content-Disposition"] = 'attachment; filename="%s"' % (
    #             file_location
    #         )
    #     return response
