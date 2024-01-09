import traceback
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import (
    CarbureLot,
    CarbureLotComment,
    Entity,
)


class AdminControlsLotsCommentError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


@check_admin_rights()
def add_comment(request, *args, **kwargs):
    try:
        entity_id = request.POST.get("entity_id")
        selection = request.POST.getlist("selection", [])
        comment = request.POST.get("comment", False)
        is_visible_by_auditor = request.POST.get("is_visible_by_auditor") == "true"
    except:
        traceback.print_exc()
        return ErrorResponse(400, AdminControlsLotsCommentError.MALFORMED_PARAMS)

    entity = Entity.objects.get(id=entity_id)
    lots = CarbureLot.objects.filter(id__in=selection)
    for lot in lots.iterator():
        lot_comment = CarbureLotComment()
        lot_comment.entity = entity
        lot_comment.user = request.user
        lot_comment.lot = lot
        lot_comment.comment_type = CarbureLotComment.ADMIN
        lot_comment.is_visible_by_admin = True
        lot_comment.is_visible_by_auditor = is_visible_by_auditor
        lot_comment.comment = comment
        lot_comment.save()

    return SuccessResponse()
