from collections import defaultdict
from functools import partial

from django.db.models import (
    Case,
    CharField,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Max,
    Min,
    Q,
    Sum,
    Value,
    When,
)

from core.models import Biocarburant
from tiruert.models import Operation
from tiruert.models.operation_detail import OperationDetail


def _get_sector_expression():
    return Case(
        When(operation__biofuel__compatible_essence=True, then=Value(Operation.ESSENCE)),
        When(operation__biofuel__compatible_diesel=True, then=Value(Operation.GAZOLE)),
        default=Value(Operation.CARBUREACTEUR),
        output_field=CharField(),
    )


def _get_teneur_sector_expression(sector_expr):
    return Case(
        When(
            Q(operation__type=Operation.TENEUR) & Q(operation__objective_sector__isnull=False),
            then=F("operation__objective_sector"),
        ),
        default=sector_expr,
        output_field=CharField(),
    )


def _get_quantity_expression(unit):
    if unit == "mj":
        factor_expr = F("operation__biofuel__pci_litre")
    elif unit == "gj":
        factor_expr = ExpressionWrapper(F("operation__biofuel__pci_litre") * Value(0.001), output_field=FloatField())
    elif unit == "kg":
        factor_expr = F("operation__biofuel__masse_volumique")
    else:
        factor_expr = Value(1.0)

    return ExpressionWrapper(
        F("volume") * F("operation__renewable_energy_share") * factor_expr,
        output_field=FloatField(),
    )


def _get_avoided_emissions_expression():
    from tiruert.services.teneur import GHG_REFERENCE_RED_II

    return ExpressionWrapper(
        (Value(GHG_REFERENCE_RED_II) - F("emission_rate_per_mj"))
        * F("lot__biofuel__pci_litre")
        * F("volume")
        * F("operation__renewable_energy_share")
        / Value(1000000.0),
        output_field=FloatField(),
    )


def _apply_detail_filters(details_qs, detail_filters=None):
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


def _build_common_context(entity_id, unit, date_from):
    quantity_expr = _get_quantity_expression(unit)
    avoided_emissions_expr = _get_avoided_emissions_expression()

    credit_cond = Q(operation__credited_entity_id=entity_id)
    debit_cond = Q(operation__debited_entity_id=entity_id)
    pending_or_draft_cond = Q(operation__status__in=[Operation.PENDING, Operation.DRAFT])
    process_cond = ~Q(operation__credited_entity_id=entity_id, operation__status__in=[Operation.PENDING, Operation.DRAFT])
    date_cond = Q() if date_from is None else Q(operation__created_at__gte=date_from)

    return {
        "quantity_expr": quantity_expr,
        "avoided_emissions_expr": avoided_emissions_expr,
        "credit_cond": credit_cond,
        "debit_cond": debit_cond,
        "pending_or_draft_cond": pending_or_draft_cond,
        "process_cond": process_cond,
        "date_cond": date_cond,
    }


def _build_base_aggregations(context, include_ghg=False):
    aggregations = {
        "available_balance": Sum(
            Case(
                When(context["process_cond"] & context["credit_cond"], then=context["quantity_expr"]),
                When(context["process_cond"] & context["debit_cond"], then=-context["quantity_expr"]),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "saved_emissions": Sum(
            Case(
                When(context["process_cond"] & context["credit_cond"], then=context["avoided_emissions_expr"]),
                When(context["process_cond"] & context["debit_cond"], then=-context["avoided_emissions_expr"]),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "quantity_credit": Sum(
            Case(
                When(
                    context["process_cond"] & context["date_cond"] & context["credit_cond"],
                    then=context["quantity_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "quantity_debit": Sum(
            Case(
                When(
                    context["process_cond"] & context["date_cond"] & context["debit_cond"],
                    then=context["quantity_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "pending_operations": Count(
            "operation_id",
            filter=context["pending_or_draft_cond"],
            distinct=True,
        ),
    }

    if include_ghg:
        aggregations["ghg_reduction_min"] = Min("lot__ghg_reduction_red_ii")
        aggregations["ghg_reduction_max"] = Max("lot__ghg_reduction_red_ii")

    return aggregations


def _build_teneur_aggregations(context):
    return {
        "pending_teneur": Sum(
            Case(
                When(
                    context["process_cond"]
                    & context["date_cond"]
                    & Q(operation__type=Operation.TENEUR)
                    & Q(operation__status=Operation.PENDING),
                    then=context["quantity_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "declared_teneur": Sum(
            Case(
                When(
                    context["process_cond"]
                    & context["date_cond"]
                    & Q(operation__type=Operation.TENEUR)
                    & Q(operation__status=Operation.DECLARED),
                    then=context["quantity_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "pending_saved_emissions": Sum(
            Case(
                When(
                    context["process_cond"]
                    & context["date_cond"]
                    & Q(operation__type=Operation.TENEUR)
                    & Q(operation__status=Operation.PENDING),
                    then=context["avoided_emissions_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "declared_saved_emissions": Sum(
            Case(
                When(
                    context["process_cond"]
                    & context["date_cond"]
                    & Q(operation__type=Operation.TENEUR)
                    & Q(operation__status=Operation.DECLARED),
                    then=context["avoided_emissions_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
    }


def _calculate_default_grouping(balance, details_qs, context):
    sector_expr = _get_sector_expression()
    teneur_sector_expr = _get_teneur_sector_expression(sector_expr)

    # Aggregate all non-teneur balance metrics (including GHG min/max) by sector/category/biofuel.
    base_groups = list(
        details_qs.annotate(
            group_sector=sector_expr,
            group_customs_category=F("operation__customs_category"),
            group_biofuel_id=F("operation__biofuel_id"),
        )
        .values("group_sector", "group_customs_category", "group_biofuel_id")
        .annotate(**_build_base_aggregations(context, include_ghg=True))
    )

    # Aggregate teneur-specific metrics separately, using objective sector when provided.
    teneur_groups = list(
        details_qs.annotate(
            group_sector=teneur_sector_expr,
            group_customs_category=F("operation__customs_category"),
            group_biofuel_id=F("operation__biofuel_id"),
        )
        .values("group_sector", "group_customs_category", "group_biofuel_id")
        .annotate(**_build_teneur_aggregations(context))
    )

    biofuel_ids = {
        group["group_biofuel_id"] for group in base_groups + teneur_groups if group["group_biofuel_id"] is not None
    }
    biofuels_by_id = Biocarburant.objects.in_bulk(biofuel_ids)

    for group in base_groups:
        biofuel = biofuels_by_id.get(group["group_biofuel_id"])
        biofuel_code = biofuel.code if biofuel else None
        key = (group["group_sector"], group["group_customs_category"], biofuel_code)

        entry = balance[key]
        entry["sector"] = group["group_sector"]
        entry["customs_category"] = group["group_customs_category"]
        entry["biofuel"] = biofuel
        entry["quantity"]["credit"] = round(group["quantity_credit"] or 0.0, 2)
        entry["quantity"]["debit"] = round(group["quantity_debit"] or 0.0, 2)
        entry["available_balance"] = round(group["available_balance"] or 0.0, 2)
        entry["saved_emissions"] = round(group["saved_emissions"] or 0.0, 2)
        entry["pending_operations"] = group["pending_operations"] or 0
        entry["ghg_reduction_min"] = group["ghg_reduction_min"]
        entry["ghg_reduction_max"] = group["ghg_reduction_max"]

    for group in teneur_groups:
        biofuel = biofuels_by_id.get(group["group_biofuel_id"])
        biofuel_code = biofuel.code if biofuel else None
        key = (group["group_sector"], group["group_customs_category"], biofuel_code)

        entry = balance[key]
        entry["sector"] = group["group_sector"]
        entry["customs_category"] = group["group_customs_category"]
        entry["biofuel"] = biofuel
        entry["pending_teneur"] = round(group["pending_teneur"] or 0.0, 2)
        entry["declared_teneur"] = round(group["declared_teneur"] or 0.0, 2)
        entry["pending_saved_emissions"] = round(group["pending_saved_emissions"] or 0.0, 2)
        entry["declared_saved_emissions"] = round(group["declared_saved_emissions"] or 0.0, 2)


def _calculate_category_grouping(balance, details_qs, context):
    category_groups = (
        details_qs.annotate(group_key=F("operation__customs_category"))
        .values("group_key")
        .annotate(
            **_build_base_aggregations(context),
            **_build_teneur_aggregations(context),
        )
    )

    for group in category_groups:
        key = group["group_key"]
        entry = balance[key]
        entry["customs_category"] = key
        entry["quantity"]["credit"] = round(group["quantity_credit"] or 0.0, 2)
        entry["quantity"]["debit"] = round(group["quantity_debit"] or 0.0, 2)
        entry["available_balance"] = round(group["available_balance"] or 0.0, 2)
        entry["saved_emissions"] = round(group["saved_emissions"] or 0.0, 2)
        entry["pending_teneur"] = round(group["pending_teneur"] or 0.0, 2)
        entry["declared_teneur"] = round(group["declared_teneur"] or 0.0, 2)
        entry["pending_saved_emissions"] = round(group["pending_saved_emissions"] or 0.0, 2)
        entry["declared_saved_emissions"] = round(group["declared_saved_emissions"] or 0.0, 2)
        entry["pending_operations"] = group["pending_operations"] or 0


def _calculate_sector_grouping(balance, details_qs, context):
    sector_expr = _get_sector_expression()
    teneur_sector_expr = _get_teneur_sector_expression(sector_expr)

    base_groups = (
        details_qs.annotate(group_key=sector_expr).values("group_key").annotate(**_build_base_aggregations(context))
    )

    for group in base_groups:
        key = group["group_key"]
        entry = balance[key]
        entry["sector"] = key
        entry["quantity"]["credit"] = round(group["quantity_credit"] or 0.0, 2)
        entry["quantity"]["debit"] = round(group["quantity_debit"] or 0.0, 2)
        entry["available_balance"] = round(group["available_balance"] or 0.0, 2)
        entry["saved_emissions"] = round(group["saved_emissions"] or 0.0, 2)
        entry["pending_operations"] = group["pending_operations"] or 0

    teneur_groups = (
        details_qs.annotate(group_key=teneur_sector_expr).values("group_key").annotate(**_build_teneur_aggregations(context))
    )

    for group in teneur_groups:
        key = group["group_key"]
        entry = balance[key]
        entry["sector"] = key
        entry["pending_teneur"] = round(group["pending_teneur"] or 0.0, 2)
        entry["declared_teneur"] = round(group["declared_teneur"] or 0.0, 2)
        entry["pending_saved_emissions"] = round(group["pending_saved_emissions"] or 0.0, 2)
        entry["declared_saved_emissions"] = round(group["declared_saved_emissions"] or 0.0, 2)


def calculate_balance_with_annotations(operations, entity_id, group_by, unit, date_from, detail_filters, init_entry):
    balance = defaultdict(partial(init_entry, unit))

    details_qs = OperationDetail.objects.filter(
        operation__in=operations,
        operation__status__in=Operation.ACTIVE_STATUSES,
    )
    details_qs = _apply_detail_filters(details_qs, detail_filters)

    context = _build_common_context(entity_id, unit, date_from)

    if group_by == "sector":
        _calculate_sector_grouping(balance, details_qs, context)
        return balance

    if group_by == "customs_category":
        _calculate_category_grouping(balance, details_qs, context)
        return balance

    _calculate_default_grouping(balance, details_qs, context)
    return balance
