import pandas as pd
from django.db.models import Q

from core.models import CarbureLot, GenericError


def create_error(error: str, emission_category: str, lot_id: int):
    return GenericError(
        error=error,
        display_to_creator=False,
        display_to_recipient=False,
        display_to_admin=True,
        display_to_auditor=True,
        is_blocking=False,
        lot_id=lot_id,
        field=emission_category,
    )


def create_errors(outliers_by_emission_category: dict[str, pd.DataFrame]):
    processed_lots = CarbureLot.objects.exclude(lot_status__in=["DRAFT", "DELETED"]).filter(
        # production_site_commissioning_date__lte="2025-01-01",
        # delivery_date__gt="1970-01-01",
        production_site_commissioning_date__gt="1970-01-01",
        delivery_date__gte="2022-03-01",
    )

    errors: list[GenericError] = []

    for emission_category, outliers in outliers_by_emission_category.items():
        lof_outlier_filters = Q()
        lof_outliers = outliers[outliers["is_lof_outlier"]].drop(columns=["is_lof_outlier", "is_if_outlier"])
        for _, row in lof_outliers.iterrows():
            filters = row.to_dict()
            lof_outlier_filters |= Q(**filters)

        lof_outlier_lot_ids = processed_lots.filter(lof_outlier_filters).distinct().values_list("id", flat=True)
        errors += [create_error("LOF_OUTLIER", emission_category, lot_id) for lot_id in lof_outlier_lot_ids]

        if_outlier_filters = Q()
        if_outliers = outliers[outliers["is_if_outlier"]].drop(columns=["is_lof_outlier", "is_if_outlier"])
        for _, row in if_outliers.iterrows():
            filters = row.to_dict()
            if_outlier_filters |= Q(**filters)

        if_outlier_lot_ids = processed_lots.filter(if_outlier_filters).distinct().values_list("id", flat=True)
        errors += [create_error("IF_OUTLIER", emission_category, lot_id) for lot_id in if_outlier_lot_ids]

    lot_ids: list[int] = [e.lot_id for e in errors]
    GenericError.objects.filter(error__in=["LOF_OUTLIER", "IF_OUTLIER"], lot_id__in=lot_ids).delete()
    GenericError.objects.bulk_create(errors, batch_size=1000)

    return lot_ids
