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
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models import Operation
from tiruert.models.operation_detail import OperationDetail
from tiruert.services.balance_filters import apply_operation_detail_filters
from tiruert.services.energy import (
    avoided_emissions_tco2_expression,
    energy_mj_expression,
)


def _get_sector_expression():
    return Case(
        When(operation__biofuel__compatible_essence=True, then=Value(Operation.ESSENCE)),
        When(operation__biofuel__compatible_diesel=True, then=Value(Operation.GAZOLE)),
        When(operation__biofuel__code__in=SAF_BIOFUEL_TYPES, then=Value(Operation.CARBUREACTEUR)),
        When(operation__biofuel__compatible_gpl=True, then=Value(Operation.GPL_C)),
        default=Value(None),
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
        return energy_mj_expression(
            F("volume"),
            F("operation__renewable_energy_share"),
            F("operation__biofuel__pci_litre"),
        )
    else:
        return ExpressionWrapper(
            F("volume"),
            output_field=FloatField(),
        )


def _get_avoided_emissions_expression():
    from tiruert.services.teneur import GHG_REFERENCE_RED_II

    energy_expr = energy_mj_expression(
        F("volume"),
        F("operation__renewable_energy_share"),
        F("lot__biofuel__pci_litre"),
    )
    return avoided_emissions_tco2_expression(
        energy_expr,
        F("emission_rate_per_mj"),
        GHG_REFERENCE_RED_II,
    )


def _build_common_context(entity_id, unit, declaration_year=None):
    quantity_expr = _get_quantity_expression(unit)
    teneur_energy_expr = _get_quantity_expression("mj")
    avoided_emissions_expr = _get_avoided_emissions_expression()

    credit_cond = Q(operation__credited_entity_id=entity_id)
    debit_cond = Q(operation__debited_entity_id=entity_id)
    pending_or_draft_cond = Q(operation__status__in=[Operation.PENDING, Operation.DRAFT])
    process_cond = ~Q(operation__credited_entity_id=entity_id, operation__status__in=[Operation.PENDING, Operation.DRAFT])
    teneur_date_cond = Q()
    if declaration_year is not None:
        teneur_date_cond = Q(operation__declaration_year=declaration_year)

    return {
        "unit": unit,
        "quantity_expr": quantity_expr,
        "teneur_energy_expr": teneur_energy_expr,
        "avoided_emissions_expr": avoided_emissions_expr,
        "credit_cond": credit_cond,
        "debit_cond": debit_cond,
        "pending_or_draft_cond": pending_or_draft_cond,
        "process_cond": process_cond,
        "teneur_date_cond": teneur_date_cond,
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
                    context["process_cond"] & context["credit_cond"],
                    then=context["quantity_expr"],
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ),
        "quantity_debit": Sum(
            Case(
                When(
                    context["process_cond"] & context["debit_cond"],
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


def _get_teneur_operation_contributions(details_qs, context, group_annotations, group_fields):
    operation_groups = (
        details_qs.annotate(**group_annotations)
        .filter(
            context["process_cond"]
            & context["teneur_date_cond"]
            & Q(operation__type=Operation.TENEUR)
            & Q(operation__status__in=[Operation.PENDING, Operation.DECLARED])
        )
        .values(*group_fields, "operation_id", "operation__status")
        .annotate(
            operation_energy=Sum(context["teneur_energy_expr"]),
            operation_saved_emissions=Sum(context["avoided_emissions_expr"]),
        )
    )

    grouped_contributions = defaultdict(
        lambda: {
            "pending_teneur": 0,
            "declared_teneur": 0,
            "pending_saved_emissions": 0.0,
            "declared_saved_emissions": 0.0,
        }
    )

    for group in operation_groups:
        key = tuple(group[field] for field in group_fields)
        entry = grouped_contributions[key]
        operation_energy = int(group["operation_energy"] or 0)
        operation_saved_emissions = group["operation_saved_emissions"] or 0.0

        if group["operation__status"] == Operation.PENDING:
            entry["pending_teneur"] += operation_energy
            entry["pending_saved_emissions"] += operation_saved_emissions
        elif group["operation__status"] == Operation.DECLARED:
            entry["declared_teneur"] += operation_energy
            entry["declared_saved_emissions"] += operation_saved_emissions

    return grouped_contributions


def _calculate_default_grouping(balance, details_qs, context):
    sector_expr = _get_sector_expression()
    group_fields = ("group_sector", "group_customs_category", "group_biofuel_id")
    group_annotations = {
        "group_sector": sector_expr,
        "group_customs_category": F("operation__customs_category"),
        "group_biofuel_id": F("operation__biofuel_id"),
    }

    # Aggregate all non-teneur balance metrics (including GHG min/max) by sector/category/biofuel.
    base_groups = list(
        details_qs.annotate(**group_annotations)
        .values(*group_fields)
        .annotate(**_build_base_aggregations(context, include_ghg=True))
    )

    # Aggregate teneur metrics by operation first, then sum operation-level contributions by output group.
    teneur_groups = _get_teneur_operation_contributions(
        details_qs,
        context,
        group_annotations=group_annotations,
        group_fields=group_fields,
    )

    biofuel_ids = {group["group_biofuel_id"] for group in base_groups if group["group_biofuel_id"] is not None}
    biofuel_ids.update(group_biofuel_id for _, _, group_biofuel_id in teneur_groups if group_biofuel_id is not None)
    biofuels_by_id = Biocarburant.objects.in_bulk(biofuel_ids)

    for group in base_groups:
        biofuel = biofuels_by_id.get(group["group_biofuel_id"])
        biofuel_code = biofuel.code if biofuel else None
        key = (group["group_sector"], group["group_customs_category"], biofuel_code)

        entry = balance[key]
        entry["sector"] = group["group_sector"]
        entry["customs_category"] = group["group_customs_category"]
        entry["biofuel"] = biofuel
        entry["quantity"]["credit"] = group["quantity_credit"] or 0.0
        entry["quantity"]["debit"] = group["quantity_debit"] or 0.0
        entry["available_balance"] = group["available_balance"] or 0.0
        entry["saved_emissions"] = group["saved_emissions"] or 0.0
        entry["pending_operations"] = group["pending_operations"] or 0
        entry["ghg_reduction_min"] = group["ghg_reduction_min"]
        entry["ghg_reduction_max"] = group["ghg_reduction_max"]

    for (group_sector, group_customs_category, group_biofuel_id), group in teneur_groups.items():
        biofuel = biofuels_by_id.get(group_biofuel_id)
        biofuel_code = biofuel.code if biofuel else None
        key = (group_sector, group_customs_category, biofuel_code)

        entry = balance[key]
        entry["sector"] = group_sector
        entry["customs_category"] = group_customs_category
        entry["biofuel"] = biofuel
        entry["pending_teneur"] = group["pending_teneur"] or 0.0
        entry["declared_teneur"] = group["declared_teneur"] or 0.0
        entry["pending_saved_emissions"] = group["pending_saved_emissions"] or 0.0
        entry["declared_saved_emissions"] = group["declared_saved_emissions"] or 0.0


def _calculate_category_grouping(balance, details_qs, context):
    category_groups = (
        details_qs.annotate(group_key=F("operation__customs_category"))
        .values("group_key")
        .annotate(**_build_base_aggregations(context))
    )

    teneur_groups = _get_teneur_operation_contributions(
        details_qs,
        context,
        group_annotations={"group_key": F("operation__customs_category")},
        group_fields=("group_key",),
    )

    for group in category_groups:
        key = group["group_key"]
        entry = balance[key]
        entry["customs_category"] = key
        entry["quantity"]["credit"] = group["quantity_credit"] or 0.0
        entry["quantity"]["debit"] = group["quantity_debit"] or 0.0
        entry["available_balance"] = group["available_balance"] or 0.0
        entry["saved_emissions"] = group["saved_emissions"] or 0.0
        entry["pending_operations"] = group["pending_operations"] or 0

    for (group_key,), group in teneur_groups.items():
        entry = balance[group_key]
        entry["customs_category"] = group_key
        entry["pending_teneur"] = group["pending_teneur"] or 0.0
        entry["declared_teneur"] = group["declared_teneur"] or 0.0
        entry["pending_saved_emissions"] = group["pending_saved_emissions"] or 0.0
        entry["declared_saved_emissions"] = group["declared_saved_emissions"] or 0.0


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
        entry["quantity"]["credit"] = group["quantity_credit"] or 0.0
        entry["quantity"]["debit"] = group["quantity_debit"] or 0.0
        entry["available_balance"] = group["available_balance"] or 0.0
        entry["saved_emissions"] = group["saved_emissions"] or 0.0
        entry["pending_operations"] = group["pending_operations"] or 0

    teneur_groups = _get_teneur_operation_contributions(
        details_qs,
        context,
        group_annotations={"group_key": teneur_sector_expr},
        group_fields=("group_key",),
    )

    for (key,), group in teneur_groups.items():
        entry = balance[key]
        entry["sector"] = key
        entry["pending_teneur"] = group["pending_teneur"] or 0.0
        entry["declared_teneur"] = group["declared_teneur"] or 0.0
        entry["pending_saved_emissions"] = group["pending_saved_emissions"] or 0.0
        entry["declared_saved_emissions"] = group["declared_saved_emissions"] or 0.0


def calculate_balance_with_annotations(
    operations, entity_id, group_by, unit, detail_filters, init_entry, declaration_year=None
):
    balance = defaultdict(partial(init_entry, unit))

    details_qs = OperationDetail.objects.filter(
        operation__in=operations,
        operation__status__in=Operation.ACTIVE_STATUSES,
    )
    details_qs = apply_operation_detail_filters(details_qs, detail_filters)

    context = _build_common_context(entity_id, unit, declaration_year)

    if group_by == "sector":
        _calculate_sector_grouping(balance, details_qs, context)
        return balance

    if group_by == "customs_category":
        _calculate_category_grouping(balance, details_qs, context)
        return balance

    _calculate_default_grouping(balance, details_qs, context)
    return balance
