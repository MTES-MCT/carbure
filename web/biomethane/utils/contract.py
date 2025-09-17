from biomethane.models.biomethane_contract_amendment import BiomethaneContractAmendment


def get_tracked_amendment_types(instance, validated_data):
    current_tracked_types = set(instance.tracked_amendment_types or [])
    validated_buyer = validated_data.get("buyer", None)

    if instance.cmax != validated_data.get("cmax", None) or instance.pap_contracted != validated_data.get(
        "pap_contracted", None
    ):
        current_tracked_types.add(BiomethaneContractAmendment.CMAX_PAP_UPDATE)

    if instance.cmax_annualized != validated_data.get("cmax_annualized", False):
        current_tracked_types.add(BiomethaneContractAmendment.CMAX_ANNUALIZATION)

    if validated_buyer is not None and instance.buyer != validated_buyer:
        current_tracked_types.add(BiomethaneContractAmendment.PRODUCER_BUYER_INFO_CHANGE)

    return list(current_tracked_types)
