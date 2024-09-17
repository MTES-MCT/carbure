import traceback

from django.db import transaction
from django.db.models.aggregates import Max, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.excel import ExcelResponse
from core.models import CarbureNotification, Entity, UserRights
from saf.filters import TicketSourceFilter
from saf.models import SafTicketSource, create_ticket_from_source
from saf.permissions import HasUserRights
from saf.serializers import (
    SafTicketSourceAssignmentSerializer,
    SafTicketSourceDetailsSerializer,
    SafTicketSourceGroupAssignmentSerializer,
    SafTicketSourceSerializer,
)
from saf.serializers.saf_ticket_source import export_ticket_sources_to_excel
from saf.serializers.schema import ErrorResponseSerializer


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
        file = export_ticket_sources_to_excel(tickets)
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
        queryset = self.filter_queryset(self.get_queryset())

        filter = self.request.query_params.get("filter")

        if not filter:
            raise ValidationError({"message": "No filter was specified"})

        if filter == "clients":
            column = "saf_tickets__client__name"
        elif filter == "periods":
            column = "delivery_period"
        elif filter == "feedstocks":
            column = "feedstock__code"
        elif filter == "countries_of_origin":
            column = "country_of_origin__code_pays"
        elif filter == "production_sites":
            column = "carbure_production_site__name"
        elif filter == "delivery_sites":
            column = "parent_lot__carbure_delivery_site__name"
        elif filter == "suppliers":
            column = "parent_supplier"
        else:  # raise an error for unknown filters
            raise ValidationError({"message": "Filter '%s' does not exist for ticket sources" % filter})

        queryset = queryset.annotate(
            parent_supplier=Coalesce(
                "parent_lot__carbure_supplier__name",
                "parent_lot__unknown_supplier",
                "parent_ticket__supplier__name",
            )
        )
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
    @action(
        methods=["post"],
        detail=False,
        url_path="group-assign",
        serializer_class=SafTicketSourceGroupAssignmentSerializer,
    )
    def grouped_assign(self, request, *args, **kwargs):
        entity_id = int(request.query_params.get("entity_id"))
        serializer = SafTicketSourceGroupAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket_sources_ids = serializer.validated_data["ticket_sources_ids"]
        client_id = serializer.validated_data["client_id"]
        volume = serializer.validated_data["volume"]
        agreement_reference = serializer.validated_data["agreement_reference"]
        agreement_date = serializer.validated_data["agreement_date"]
        free_field = serializer.validated_data.get("free_field")
        assignment_period = serializer.validated_data["assignment_period"]

        ticket_sources = SafTicketSource.objects.filter(id__in=ticket_sources_ids, added_by_id=entity_id).order_by(
            "created_at"
        )

        if not ticket_sources:
            return Response(
                {"message": SafTicketGroupedAssignError.TICKET_SOURCE_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            total_volume_in_selection = ticket_sources.aggregate(Sum("total_volume"))["total_volume__sum"]
            assigned_volume_in_selection = ticket_sources.aggregate(Sum("assigned_volume"))["assigned_volume__sum"]
            if volume > (total_volume_in_selection - assigned_volume_in_selection):
                return Response(
                    {"message": SafTicketGroupedAssignError.VOLUME_TOO_BIG},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # use the most recent period of all the selected ticket sources to decide if the asked period is ok
            most_recent_period = ticket_sources.aggregate(Max("delivery_period"))["delivery_period__max"]
            if assignment_period < most_recent_period:
                return Response(
                    {"message": SafTicketGroupedAssignError.ASSIGNMENT_BEFORE_DELIVERY},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                assigned_tickets_count = 0
                remaining_volume_to_assign = volume

                for ticket_source in ticket_sources:
                    # create a ticket with a volume taking into account:
                    # - what's left in the ticket source
                    available_volume_in_source = ticket_source.total_volume - ticket_source.assigned_volume
                    # - and what's left in the amount asked by the user
                    ticket_volume = min(remaining_volume_to_assign, available_volume_in_source)

                    # do not
                    if ticket_volume <= 0:
                        break

                    ticket = create_ticket_from_source(
                        ticket_source,
                        client_id=client_id,
                        volume=ticket_volume,
                        agreement_date=agreement_date,
                        agreement_reference=agreement_reference,
                        assignment_period=assignment_period,
                        free_field=free_field,
                    )

                    CarbureNotification.objects.create(
                        type=CarbureNotification.SAF_TICKET_RECEIVED,
                        dest_id=client_id,
                        send_by_email=False,
                        meta={
                            "supplier": ticket.supplier.name,
                            "ticket_id": ticket.id,
                            "year": ticket.year,
                        },
                    )

                    assigned_tickets_count += 1
                    ticket_source.assigned_volume += ticket.volume
                    remaining_volume_to_assign -= ticket.volume
                    ticket_source.save()

            return Response(
                {"assigned_tickets_count": assigned_tickets_count},
                status=status.HTTP_200_OK,
            )
        except Exception:
            traceback.print_exc()
            raise ValidationError({"message": SafTicketGroupedAssignError.TICKET_CREATION_FAILED})

    @extend_schema(
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(
        methods=["post"],
        detail=True,
        serializer_class=SafTicketSourceAssignmentSerializer,
    )
    def assign(self, request, id=None):
        entity_id = int(request.query_params.get("entity_id"))
        ticket_source = get_object_or_404(SafTicketSource, id=id, added_by_id=entity_id)

        serializer = SafTicketSourceAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = serializer.validated_data["client_id"]
        volume = serializer.validated_data["volume"]
        agreement_reference = serializer.validated_data["agreement_reference"]
        agreement_date = serializer.validated_data["agreement_date"]
        free_field = serializer.validated_data.get("free_field")
        assignment_period = serializer.validated_data["assignment_period"]

        if volume > (ticket_source.total_volume - ticket_source.assigned_volume):
            raise ValidationError({"message": SafTicketGroupedAssignError.VOLUME_TOO_BIG})

        if assignment_period < ticket_source.delivery_period:
            raise ValidationError({"message": SafTicketGroupedAssignError.ASSIGNMENT_BEFORE_DELIVERY})

        try:
            with transaction.atomic():
                ticket = create_ticket_from_source(
                    ticket_source,
                    client_id=client_id,
                    volume=volume,
                    agreement_date=agreement_date,
                    agreement_reference=agreement_reference,
                    assignment_period=assignment_period,
                    free_field=free_field,
                )

                CarbureNotification.objects.create(
                    type=CarbureNotification.SAF_TICKET_RECEIVED,
                    dest_id=client_id,
                    send_by_email=False,
                    meta={
                        "supplier": ticket.supplier.name,
                        "ticket_id": ticket.id,
                        "year": ticket.year,
                    },
                )

                ticket_source.assigned_volume += ticket.volume
                ticket_source.save()

            return Response({}, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            raise ValidationError({"message": SafTicketGroupedAssignError.TICKET_CREATION_FAILED})


class SafTicketGroupedAssignError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    VOLUME_TOO_BIG = "VOLUME_TOO_BIG"
    TICKET_CREATION_FAILED = "TICKET_CREATION_FAILED"
    TICKET_SOURCE_NOT_FOUND = "TICKET_SOURCE_NOT_FOUND"
    ASSIGNMENT_BEFORE_DELIVERY = "ASSIGNMENT_BEFORE_DELIVERY"


class SafTicketSourceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR]),
    )
    serializer_class = SafTicketSourceSerializer
    filterset_class = TicketSourceFilter
    search_fields = [
        "carbure_id",
        "saf_tickets__client__name",
        "feedstock__name",
        "biofuel__name",
        "country_of_origin__name",
        "carbure_production_site__name",
        "unknown_production_site",
    ]

    def get_permissions(self):
        if self.action in ["grouped_assign", "assign"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.OPERATOR])]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SafTicketSourceDetailsSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = SafTicketSource.objects.none()
        if self.request and not self.request.user.is_anonymous:
            queryset = (
                SafTicketSource.objects.select_related(
                    "feedstock",
                    "biofuel",
                    "country_of_origin",
                    "carbure_production_site",
                )
                .prefetch_related("saf_tickets")
                .prefetch_related("saf_tickets__client")
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
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
