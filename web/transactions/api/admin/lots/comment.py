from django import forms

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import (
    CarbureLot,
    CarbureLotComment,
)
from core.utils import MultipleValueField


class AdminControlsLotsCommentForm(forms.Form):
    comment = forms.CharField()
    selection = MultipleValueField(coerce=int, required=False)
    is_visible_by_auditor = forms.BooleanField(required=False)


@check_admin_rights()
def add_comment(request, entity):
    form = AdminControlsLotsCommentForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    is_visible_by_auditor = form.cleaned_data["is_visible_by_auditor"]
    comment = form.cleaned_data["comment"]
    selection = form.cleaned_data["selection"]

    lots = CarbureLot.objects.filter(id__in=selection)
    for lot in lots:
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
