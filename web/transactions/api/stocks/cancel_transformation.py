from django import forms
from django.db import transaction
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureStock, CarbureStock, CarbureStockEvent, CarbureStockTransformation, UserRights
from core.utils import MultipleValueField


class StockCancelTransformationForm(forms.Form):
    stock_ids = MultipleValueField(coerce=int)


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_cancel_transformation(request, entity):
    form = StockCancelTransformationForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, data=form.errors)

    stock_ids = form.cleaned_data["stock_ids"]

    stocks = (
        CarbureStock.objects.filter(pk__in=stock_ids, carbure_client=entity)
        .exclude(parent_transformation=None)
        .select_related("parent_transformation", "parent_transformation__source_stock")
    )

    with transaction.atomic():
        stock_events = []
        stocks_to_update = set()

        stock_transformations = [s.parent_transformation for s in stocks]

        for transform in stock_transformations:
            transform.source_stock.update_remaining_volume(+transform.volume_deducted_from_source)

            stocks_to_update.add(transform.source_stock)

            stock_events.append(
                CarbureStockEvent(
                    stock=transform.source_stock,
                    event_type=CarbureStockEvent.UNTRANSFORMED,
                    user=request.user,
                )
            )

        CarbureStockEvent.objects.bulk_create(stock_events)
        CarbureStock.objects.bulk_update(stocks_to_update, ["remaining_volume", "remaining_weight", "remaining_lhv_amount"])
        CarbureStockTransformation.objects.filter(id__in=[t.id for t in stock_transformations]).delete()

    return SuccessResponse()
