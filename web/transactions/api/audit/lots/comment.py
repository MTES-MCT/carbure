from django.http.response import JsonResponse

from core.decorators import check_user_rights
from core.models import CarbureLot, CarbureLotComment, Entity


@check_user_rights(entity_type=[Entity.AUDITOR])
def add_comment(request, entity, entity_id):
    selection = request.POST.getlist("selection", [])
    comment = request.POST.get("comment", False)
    is_visible_by_admin = request.POST.get("is_visible_by_admin") == "true"

    if not comment:
        return JsonResponse({"status": "error", "message": "Missing comment"}, status=400)

    entity = Entity.objects.get(id=entity_id)
    lots = CarbureLot.objects.filter(id__in=selection)
    for lot in lots:
        lot_comment = CarbureLotComment()
        lot_comment.entity = entity
        lot_comment.user = request.user
        lot_comment.lot = lot
        lot_comment.comment_type = CarbureLotComment.AUDITOR
        lot_comment.is_visible_by_auditor = True
        lot_comment.is_visible_by_admin = is_visible_by_admin
        lot_comment.comment = comment
        lot_comment.save()

    return JsonResponse({"status": "success"})
