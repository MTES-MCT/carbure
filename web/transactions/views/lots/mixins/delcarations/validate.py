import traceback

from django.db import transaction
from django.db.models.query_utils import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from carbure.tasks import (
    background_bulk_sanity_checks,
    background_bulk_scoring,
    background_create_ticket_sources_from_lots,
)
from core.carburetypes import CarbureError
from core.helpers import send_email_declaration_validated
from core.models import CarbureLot, CarbureLotEvent, SustainabilityDeclaration
from core.notifications import notify_declaration_validated
from transactions.helpers import check_locked_year


class ValidateDeclarationSerializer(serializers.Serializer):
    period = serializers.IntegerField()


class ValidateDeclarationError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    DECLARATION_CANNOT_BE_CREATED = "DECLARATION_CANNOT_BE_CREATED"
    SOME_LOTS_ARE_PENDING = "SOME_LOTS_ARE_PENDING"
    SOME_LOTS_ARE_IN_CORRECTION = "SOME_LOTS_ARE_IN_CORRECTION"
    SOME_LOTS_ARE_REJECTED = "SOME_LOTS_ARE_REJECTED"


class ValidateDeclarationActionMixin:
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
        request=ValidateDeclarationSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="declarations-validate")
    def validate_declaration(self, request, *args, **kwargs):
        entity_id = request.query_params.get("entity_id")
        serializer = ValidateDeclarationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        period = serializer.validated_data["period"]

        year = int(period / 100)
        if check_locked_year(year):
            raise ValidationError({"message": CarbureError.YEAR_LOCKED})

        try:
            declaration = SustainabilityDeclaration.init_declaration(entity_id, period)
        except Exception:
            traceback.print_exc()
            raise ValidationError({"message": ValidateDeclarationError.DECLARATION_CANNOT_BE_CREATED})

        # grab the list of all the lots related to this declaration
        declaration_lots = (
            CarbureLot.objects.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
            .filter(period=period)
            .filter(Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id))
        )

        pending_lots = declaration_lots.filter(lot_status=CarbureLot.PENDING)
        if pending_lots.count() > 0:
            raise ValidationError({"message": ValidateDeclarationError.SOME_LOTS_ARE_PENDING})

        in_correction_lots = declaration_lots.filter(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])
        if in_correction_lots.count() > 0:
            raise ValidationError({"message": ValidateDeclarationError.SOME_LOTS_ARE_IN_CORRECTION})

        rejected_lots = declaration_lots.filter(lot_status=CarbureLot.REJECTED)
        if rejected_lots.count() > 0:
            raise ValidationError({"message": ValidateDeclarationError.SOME_LOTS_ARE_REJECTED})

        with transaction.atomic():
            # Mark the sent lots of this declaration as declared by the supplier
            sent_lots = declaration_lots.filter(carbure_supplier_id=entity_id)
            sent_lots.update(declared_by_supplier=True)

            # if the client on some sent lots is unknown, mark them as declared by the client
            unknown_client_lots = sent_lots.filter(carbure_client=None)
            unknown_client_lots.update(declared_by_client=True)

            # Mark the received lots of this declaration as declared by the client
            received_lots = declaration_lots.filter(carbure_client_id=entity_id)
            received_lots.update(declared_by_client=True)

            # if the supplier on some received lots is unknown, mark them as declared by the supplier
            unknown_supplier_lots = received_lots.filter(carbure_supplier=None)
            unknown_supplier_lots.update(declared_by_supplier=True)

            # Create SAF ticket sources for declared received lots
            background_create_ticket_sources_from_lots(received_lots)

            # Freeze lots that are marked as declared by both supplier and client
            declared_lots = declaration_lots.filter(declared_by_supplier=True, declared_by_client=True)
            declared_lots.update(lot_status=CarbureLot.FROZEN)

            # Mark declaration as complete
            declaration.declared = True
            declaration.save()

            # Create declaration events for all these lots
            bulk_events = []
            for lot in declared_lots:
                bulk_events.append(CarbureLotEvent(event_type=CarbureLotEvent.DECLARED, lot=lot, user=request.user))
            CarbureLotEvent.objects.bulk_create(bulk_events)

            background_bulk_scoring(declared_lots)

            # check if there are lots being created/fixed for that period and lock them
            declaration_lots_editing = (
                CarbureLot.objects.filter(period=period)
                .filter(Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id))
                .filter(Q(lot_status=CarbureLot.DRAFT) | Q(correction_status=CarbureLot.IN_CORRECTION))
            )
            background_bulk_sanity_checks(declaration_lots_editing)

            # Send confirmation email and notification
            notify_declaration_validated(declaration)
            send_email_declaration_validated(declaration, request)

        return Response({"status": "success"})
