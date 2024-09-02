from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.helpers import (
    filter_lots,
    get_entity_lots_by_status,
)
from core.models import (
    CarbureLotComment,
    Entity,
    UserRights,
)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_comment(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    status = request.POST.get("status", False)
    comment = request.POST.get("comment", False)
    if not comment:
        return JsonResponse({"status": "error", "message": "Missing comment"}, status=400)
    is_visible_by_admin = request.POST.get("is_visible_by_admin", False)
    is_visible_by_auditor = request.POST.get("is_visible_by_auditor", False)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity)

    for lot in lots:
        if (
            lot.carbure_supplier != entity
            and lot.carbure_client != entity
            and entity.entity_type not in [Entity.AUDITOR, Entity.ADMIN]
        ):
            return JsonResponse(
                {
                    "status": "forbidden",
                    "message": "Entity not authorized to comment on this lot",
                },
                status=403,
            )

        lot_comment = CarbureLotComment()
        lot_comment.entity = entity
        lot_comment.user = request.user
        lot_comment.lot = lot
        if entity.entity_type == Entity.AUDITOR:
            lot_comment.comment_type = CarbureLotComment.AUDITOR
            if is_visible_by_admin == "true":
                lot_comment.is_visible_by_admin = True
        elif entity.entity_type == Entity.ADMIN:
            lot_comment.comment_type = CarbureLotComment.ADMIN
            if is_visible_by_auditor == "true":
                lot_comment.is_visible_by_auditor = True
        else:
            lot_comment.comment_type = CarbureLotComment.REGULAR
        lot_comment.comment = comment
        lot_comment.save()
    return JsonResponse({"status": "success"})
