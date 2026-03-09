from django.utils.translation import gettext as _

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights
from transactions.services.lots import LotCreationFailure, create_lot


class AddLotError:
    LOT_CREATION_FAILED = ("LOT_CREATION_FAILED", _("Le lot n'a pas pu être créé."))


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_lot(request, entity):
    lot_data = request.POST.dict()
    user = request.user

    try:
        created_lot_data = create_lot(user, entity, "MANUAL", lot_data)
        return SuccessResponse(created_lot_data)
    except LotCreationFailure:
        return ErrorResponse(400, AddLotError.LOT_CREATION_FAILED)
