import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from saf.models import SafTicket
from saf.serializers.schema import CommentSerializer, ErrorResponseSerializer

from .utils import SafTicketError


class CancelActionMixin:
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
