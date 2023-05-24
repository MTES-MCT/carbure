import traceback

from core.helpers import send_email_declaration_validated
from carbure.tasks import (
    background_bulk_scoring,
    background_create_ticket_sources_from_lots,
)
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import (
    CarbureLot,
    CarbureLotEvent,
    SustainabilityDeclaration,
    UserRights,
)
from core.notifications import notify_declaration_validated
from django.db import transaction
from django.db.models import Q
from transactions.helpers import check_locked_year


class ValidateDeclarationError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    DECLARATION_CANNOT_BE_CREATED = "DECLARATION_CANNOT_BE_CREATED"
    SOME_LOTS_ARE_PENDING = "SOME_LOTS_ARE_PENDING"
    SOME_LOTS_ARE_IN_CORRECTION = "SOME_LOTS_ARE_IN_CORRECTION"
    SOME_LOTS_ARE_REJECTED = "SOME_LOTS_ARE_REJECTED"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def validate_declaration(request, *args, **kwargs):
    try:
        entity_id = int(request.POST.get("entity_id", None))
        period = int(request.POST.get("period", None))
    except:
        traceback.print_exc()
        return ErrorResponse(400, ValidateDeclarationError.MALFORMED_PARAMS)

    year = int(period / 100)
    if check_locked_year(year):
        return ErrorResponse(400, CarbureError.YEAR_LOCKED)

    try:
        declaration = SustainabilityDeclaration.init_declaration(entity_id, period)
    except:
        traceback.print_exc()
        return ErrorResponse(
            400, ValidateDeclarationError.DECLARATION_CANNOT_BE_CREATED
        )

    # grab the list of all the lots related to this declaration
    declaration_lots = (
        CarbureLot.objects.exclude(
            lot_status__in=(CarbureLot.DRAFT, CarbureLot.DELETED)
        )
        .filter(period=period)
        .filter(Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id))
    )

    pending_lots = declaration_lots.filter(lot_status=CarbureLot.PENDING)
    if pending_lots.count() > 0:
        return ErrorResponse(400, ValidateDeclarationError.SOME_LOTS_ARE_PENDING)

    in_correction_lots = declaration_lots.filter(
        correction_status__in=(CarbureLot.IN_CORRECTION, CarbureLot.FIXED)
    )
    if in_correction_lots.count() > 0:
        return ErrorResponse(400, ValidateDeclarationError.SOME_LOTS_ARE_IN_CORRECTION)

    rejected_lots = declaration_lots.filter(lot_status=CarbureLot.REJECTED)
    if rejected_lots.count() > 0:
        return ErrorResponse(400, ValidateDeclarationError.SOME_LOTS_ARE_REJECTED)

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
        declared_lots = declaration_lots.filter(
            declared_by_supplier=True, declared_by_client=True
        )
        declared_lots.update(lot_status=CarbureLot.FROZEN)

        # Mark declaration as complete
        declaration.declared = True
        declaration.save()

        # Create declaration events for all these lots
        bulk_events = []
        for lot in declared_lots:
            bulk_events.append(
                CarbureLotEvent(
                    event_type=CarbureLotEvent.DECLARED, lot=lot, user=request.user
                )
            )
        CarbureLotEvent.objects.bulk_create(bulk_events)

        background_bulk_scoring(declared_lots)

        # Send confirmation email and notification
        notify_declaration_validated(declaration)
        send_email_declaration_validated(declaration)

    return SuccessResponse()
