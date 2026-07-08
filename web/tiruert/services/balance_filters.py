def apply_operation_detail_filters(details_qs, detail_filters=None):
    if not detail_filters:
        return details_qs

    ges_min = detail_filters.get("ges_bound_min")
    ges_max = detail_filters.get("ges_bound_max")
    if ges_min is not None and ges_max is not None:
        details_qs = details_qs.filter(
            lot__ghg_reduction_red_ii__gte=float(ges_min),
            lot__ghg_reduction_red_ii__lte=float(ges_max),
        )

    feedstock = detail_filters.get("feedstock")
    if feedstock:
        details_qs = details_qs.filter(lot__feedstock__code__in=feedstock)

    origin_country = detail_filters.get("origin_country")
    if origin_country:
        details_qs = details_qs.filter(lot__country_of_origin__code_pays__in=origin_country)

    lot_ids = detail_filters.get("lot_ids")
    if lot_ids is not None:
        details_qs = details_qs.filter(lot_id__in=lot_ids)

    return details_qs
