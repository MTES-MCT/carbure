from django import forms
from admin.api.controls.helpers import get_admin_lot_comments
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.helpers import (
    get_known_certificates,
    get_lot_comments,
    get_lot_errors,
    get_lot_updates,
    get_transaction_distance,
)
from core.decorators import check_admin_rights
from core.models import (
    CarbureLot,
    CarbureStock,
)
from core.serializers import (
    CarbureLotAdminSerializer,
    CarbureLotReliabilityScoreSerializer,
    CarbureStockPublicSerializer,
)


class AdminControlsLotsDetailsForm(forms.Form):
    lot_id = forms.ModelChoiceField(queryset=CarbureLot.objects.all())


@check_admin_rights()
def get_lot_details(request, entity):
    form = AdminControlsLotsDetailsForm(request.GET)
    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    lot = form.cleaned_data["lot_id"]

    data = {}
    data["lot"] = CarbureLotAdminSerializer(lot).data
    data["parent_lot"] = CarbureLotAdminSerializer(lot.parent_lot).data if lot.parent_lot else None
    data["parent_stock"] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
    data["children_lot"] = CarbureLotAdminSerializer(CarbureLot.objects.filter(parent_lot=lot), many=True).data
    data["children_stock"] = CarbureStockPublicSerializer(CarbureStock.objects.filter(parent_lot=lot), many=True).data
    data["distance"] = get_transaction_distance(lot)
    data["errors"] = get_lot_errors(lot, entity)
    data["certificates"] = get_known_certificates(lot)
    data["updates"] = get_lot_updates(lot)
    data["comments"] = get_lot_comments(lot)
    data["control_comments"] = get_admin_lot_comments(lot)
    data["score"] = CarbureLotReliabilityScoreSerializer(lot.carburelotreliabilityscore_set.all(), many=True).data
    return SuccessResponse(data)
