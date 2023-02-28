import traceback
from django.db.models import Q
from django.db import transaction
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from carbure.tasks import background_bulk_scoring
from core.notifications import notify_declaration_cancelled
from api.v4.helpers import send_email_declaration_invalidated

from core.models import UserRights, SustainabilityDeclaration, CarbureLot, CarbureLotEvent


class InvalidateDeclarationError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    DECLARATION_CANNOT_BE_CREATED = "DECLARATION_CANNOT_BE_CREATED"


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def invalidate_declaration(request, *args, **kwargs):
    try:
        entity_id = int(request.POST.get("entity_id", None))
        period = int(request.POST.get("period", None))
    except:
        traceback.print_exc()
        return ErrorResponse(400, InvalidateDeclarationError.MALFORMED_PARAMS)

    # 2. get or create a declaration entry for the given period and entity and mark it as undeclared

    try:
        declaration = SustainabilityDeclaration.init_declaration(entity_id, period)
    except:
        traceback.print_exc()
        return ErrorResponse(400, InvalidateDeclarationError.DECLARATION_CANNOT_BE_CREATED)

    # grab the list of all the lots related to this declaration
    declaration_lots = (
        CarbureLot.objects.exclude(lot_status__in=(CarbureLot.DRAFT, CarbureLot.DELETED))
        .filter(period=period)
        .filter(Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id))
    )

    with transaction.atomic():
        # Mark the sent lots of this declaration as declared by the supplier
        sent_lots = declaration_lots.filter(carbure_supplier_id=entity_id)
        sent_lots.update(declared_by_supplier=False)

        # Mark the received lots of this declaration as declared by the client
        received_lots = declaration_lots.filter(carbure_client_id=entity_id)
        received_lots.update(declared_by_client=False)

        # Unfreeze all the lots of this declaration
        undeclared_lots = sent_lots | received_lots
        undeclared_lots.update(lot_status=CarbureLot.ACCEPTED)

        # Create cancel declaration events for all these lots
        bulk_events = []
        for lot in undeclared_lots:
            bulk_events.append(CarbureLotEvent(event_type=CarbureLotEvent.DECLCANCEL, lot=lot, user=request.user))
        CarbureLotEvent.objects.bulk_create(bulk_events)

        background_bulk_scoring(undeclared_lots)

        # Update the declaration so it doesn't show as declared anymore
        declaration.declared = False
        declaration.checked = False
        declaration.save()

        # Send confirmation email
        notify_declaration_cancelled(declaration)
        send_email_declaration_invalidated(declaration)

    return SuccessResponse()