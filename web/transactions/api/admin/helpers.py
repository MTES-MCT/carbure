from core.models import (
    CarbureLot,
    CarbureLotComment,
)
from core.serializers import (
    CarbureLotCommentSerializer,
)
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q


def get_admin_summary_data(lots, short=False):
    data = {
        "count": lots.count(),
        "total_volume": lots.aggregate(Sum("volume"))["volume__sum"] or 0,
        "total_weight": lots.aggregate(Sum("weight"))["weight__sum"] or 0,
        "total_lhv_amount": lots.aggregate(Sum("lhv_amount"))["lhv_amount__sum"] or 0,
    }

    if short:
        return data

    pending_filter = Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED]) | Q(
        correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]
    )

    lots = (
        lots.annotate(
            supplier=Coalesce("carbure_supplier__name", "unknown_supplier"),
            client=Coalesce("carbure_client__name", "unknown_client"),
            biofuel_code=F("biofuel__code"),
        )
        .values("supplier", "client", "biofuel_code", "delivery_type")
        .annotate(
            volume_sum=Sum("volume"),
            weight_sum=Sum("weight"),
            lhv_amount_sum=Sum("lhv_amount"),
            avg_ghg_reduction=Sum(F("volume") * F("ghg_reduction_red_ii"))
            / Sum("volume"),
            total=Count("id"),
            pending=Count("id", filter=pending_filter),
        )
        .distinct()
        .order_by()
    )

    data["lots"] = list(lots)
    return data


def get_admin_lot_comments(lot):
    if lot is None:
        return []
    comments = lot.carburelotcomment_set.filter(
        Q(comment_type=CarbureLotComment.ADMIN) | Q(is_visible_by_admin=True)
    )
    return CarbureLotCommentSerializer(comments, many=True).data
