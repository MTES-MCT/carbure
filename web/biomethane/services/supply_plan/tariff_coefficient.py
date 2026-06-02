"""
Resolve the tariff coefficient (P1, P2, P3, P, Peff) for a supply plan input line.

The coefficient is not stored on BiomethaneSupplyInput: it is derived from the reference table
(feedstock × tariff regime) and the producer's contract.
"""

from biomethane.models import BiomethaneFeedstockTariffCoefficient, BiomethaneSupplyInput
from biomethane.services.supply_plan.supply_input import COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES


def feedstock_requires_local_collection_for_coefficient(feedstock) -> bool:
    """True when the coefficient only applies if collection is from local authorities."""
    if not feedstock:
        return False
    return getattr(feedstock, "code", None) in COLLECTION_TYPE_REQUIRED_FEEDSTOCK_CODES


def resolve_tariff_coefficient(supply_input, tariff_reference=None) -> str | None:
    """
    Return the tariff coefficient for a supply input line, or None if not applicable.

    - Regime is derived from tariff_reference (contract) via TARIFF_REFERENCE_TO_REGIME.
    - Feedstocks that require collection_type: coefficient only when collection_type == LOCAL.
    - Other feedstocks: referential coefficient with no collection_type condition.
    """
    if not supply_input.feedstock_id:
        return None

    if tariff_reference is None:
        tariff_reference = _tariff_reference_for_supply_input(supply_input)
    if not tariff_reference:
        return None

    regime = BiomethaneFeedstockTariffCoefficient.regime_for_tariff_reference(tariff_reference)
    if not regime:
        return None

    row = BiomethaneFeedstockTariffCoefficient.objects.filter(
        feedstock_id=supply_input.feedstock_id,
        regime=regime,
    ).first()
    if not row:
        return None

    if feedstock_requires_local_collection_for_coefficient(supply_input.feedstock):
        if supply_input.collection_type != BiomethaneSupplyInput.LOCAL:
            return None

    return row.coefficient


def _tariff_reference_for_supply_input(supply_input) -> str | None:
    producer = supply_input.supply_plan.producer
    contract = getattr(producer, "biomethane_contract", None)
    if not contract:
        return None
    return contract.tariff_reference
