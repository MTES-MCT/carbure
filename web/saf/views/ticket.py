import traceback

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.excel import ExcelResponse
from core.models import CarbureNotification, Entity, UserRights
from saf.filters import TicketFilter
from saf.models import SafTicket, create_source_from_ticket
from saf.permissions import HasUserRights
from saf.serializers import SafTicketDetailsSerializer, SafTicketSerializer
from saf.serializers.saf_ticket import export_tickets_to_excel
from saf.serializers.schema import CommentSerializer, ErrorResponseSerializer


class SafTicketError:
    TICKET_DETAILS_FAILED = "TICKET_DETAILS_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TICKET_REJECTION_FAILED = "TICKET_REJECTION_FAILED"
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"
    TICKET_ACCEPTANCE_FAILED = "TICKET_ACCEPTANCE_FAILED"
    TICKET_CANCELLATION_FAILED = "TICKET_CANCELLATION_FAILED"


class ActionMixin:
    @extend_schema(
        filters=True,
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="csv file.csv",
                request_only=False,
                response_only=True,
                media_type="application/vnd.ms-excel",
            ),
        ],
        responses={
            (200, "application/vnd.ms-excel"): OpenApiTypes.STR,
        },
    )
    @action(methods=["get"], detail=False)
    def export(self, request, *args, **kwargs):
        tickets = self.filter_queryset(self.get_queryset())
        file = export_tickets_to_excel(tickets)
        return ExcelResponse(file)

    @extend_schema(
        filters=True,
        examples=[
            OpenApiExample(
                "Example of filters response.",
                value=[
                    "SHELL France",
                    "CIM SNC",
                    "ESSO SAF",
                    "TMF",
                    "TERF SAF",
                ],
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["get"], detail=False)
    def filters(self, request, *args, **kwargs):
        query_params = request.GET.copy()

        filter = request.query_params.get("filter")
        entity_id = self.request.query_params.get("entity_id")

        if not filter:
            raise Exception("No filter was specified")

        if filter in query_params:
            query_params.pop(filter)

        filterset = self.filterset_class(query_params, queryset=self.get_queryset())
        queryset = filterset.qs

        filters = {
            "suppliers": "supplier__name",
            "periods": "assignment_period",
            "feedstocks": "feedstock__code",
        }
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type != Entity.AIRLINE:
            filters.update(
                {
                    "clients": "client__name",
                    "countries_of_origin": "country_of_origin__code_pays",
                    "production_sites": "carbure_production_site__name",
                }
            )

        column = filters.get(filter)
        if not column:
            raise Exception(f"Filter '{filter}' does not exist for tickets")

        values = queryset.values_list(column, flat=True).distinct()
        results = [v for v in values if v]
        data = set(results)
        return Response(list(data))

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
        responses={200: OpenApiTypes.ANY, 400: ErrorResponseSerializer},
    )
    @action(methods=["post"], detail=True, serializer_class=CommentSerializer)
    def reject(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        comment = request.data.get("comment")
        ticket = get_object_or_404(SafTicket, id=id, client_id=entity_id)

        try:
            with transaction.atomic():
                ticket.status = SafTicket.REJECTED
                ticket.client_comment = comment
                ticket.save()

                CarbureNotification.objects.create(
                    type=CarbureNotification.SAF_TICKET_REJECTED,
                    dest_id=ticket.supplier_id,
                    send_by_email=False,
                    meta={
                        "client": ticket.client.name,
                        "ticket_id": ticket.id,
                        "year": ticket.year,
                    },
                )
            return Response({}, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response(
                {"error": SafTicketError.TICKET_REJECTION_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
        responses={200: OpenApiTypes.ANY, 400: ErrorResponseSerializer},
    )
    @action(methods=["post"], detail=True, serializer_class=CommentSerializer)
    def accept(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        ticket = get_object_or_404(SafTicket, id=id, client_id=entity_id)

        try:
            with transaction.atomic():
                ticket.status = SafTicket.ACCEPTED
                ticket.save()

                create_source_from_ticket(ticket, entity_id)

                CarbureNotification.objects.create(
                    type=CarbureNotification.SAF_TICKET_ACCEPTED,
                    dest_id=ticket.supplier_id,
                    send_by_email=False,
                    meta={
                        "client": ticket.client.name,
                        "ticket_id": ticket.id,
                        "year": ticket.year,
                    },
                )

            return Response({}, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response(
                {"error": SafTicketError.TICKET_ACCEPTANCE_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
        responses={200: OpenApiTypes.ANY, 400: ErrorResponseSerializer},
    )
    @action(methods=["post"], detail=True, serializer_class=CommentSerializer)
    def cancel(self, request, id):
        entity_id = request.query_params.get("entity_id")
        ticket = get_object_or_404(SafTicket, id=id, supplier_id=entity_id)

        try:
            with transaction.atomic():
                ticket.parent_ticket_source.assigned_volume -= ticket.volume
                ticket.parent_ticket_source.save()
                ticket.delete()

            return Response({}, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response(
                {"error": SafTicketError.TICKET_CANCELLATION_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SafTicketViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR, Entity.AIRLINE]),
    )
    serializer_class = SafTicketSerializer
    filterset_class = TicketFilter
    search_fields = [
        "carbure_id",
        "supplier__name",
        "client__name",
        "feedstock__name",
        "biofuel__name",
        "country_of_origin__name",
        "agreement_reference",
        "carbure_production_site__name",
        "unknown_production_site",
    ]

    def get_permissions(self):
        if self.action in ["reject", "accept"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        if self.action == "cancel":
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.OPERATOR])]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SafTicketDetailsSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = SafTicket.objects.none()
        if self.request and not self.request.user.is_anonymous:
            queryset = SafTicket.objects.select_related(
                "parent_ticket_source",
                "feedstock",
                "biofuel",
                "country_of_origin",
                "carbure_production_site",
                "supplier",
                "client",
            )
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
        ],
    )
    def retrieve(self, request, id):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type == Entity.AIRLINE:
            ticket = SafTicket.objects.select_related("parent_ticket_source").get(id=id, client_id=entity_id)
        else:
            ticket_filter = Q(id=id) & (Q(supplier_id=entity_id) | Q(client_id=entity_id))
            ticket = get_object_or_404(SafTicket.objects.select_related("parent_ticket_source"), ticket_filter)

            if ticket.supplier_id != int(entity_id):
                ticket.parent_ticket_source = None

        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
