from collections import defaultdict
from copy import copy
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import CarbureLot, MatierePremiere
from core.models.feedstock import Biocarburant
from core.utils import truncate
from tiruert.filters import OperationFilterForBalance
from tiruert.models import Operation, OperationDetail
from tiruert.services.balance import BalanceService
from tiruert.services.energy import energy_mj
from tiruert.services.objective import ObjectiveService
from tiruert.services.teneur import TeneurService


class OperationServiceErrors:
    ENTITY_ID_DO_NOT_MATCH_DEBITED_ID = "ENTITY_ID_DO_NOT_MATCH_DEBITED_ID"
    LOT_EMISSION_RATE_NOT_FOUND = "LOT_EMISSION_RATE_NOT_FOUND"


class OperationService:
    @staticmethod
    def get_emission_rates_by_lot(lot_ids):
        """
        Return emission rates by lot_id using the oldest OperationDetail found for each lot.
        """
        details = (
            OperationDetail.objects.filter(lot_id__in=lot_ids)
            .select_related("operation")
            .order_by("lot_id", "operation__created_at", "id")
            .values_list("lot_id", "emission_rate_per_mj")
        )

        emission_rates_by_lot = {}
        for lot_id, emission_rate in details:
            if lot_id not in emission_rates_by_lot:
                emission_rates_by_lot[lot_id] = emission_rate

        missing_lot_ids = set(lot_ids) - set(emission_rates_by_lot)
        if missing_lot_ids:
            raise serializers.ValidationError(
                {
                    f"lot_id: {lot_id}": OperationServiceErrors.LOT_EMISSION_RATE_NOT_FOUND
                    for lot_id in sorted(missing_lot_ids)
                }
            )

        return emission_rates_by_lot

    @staticmethod
    def perform_checks_before_create(request, entity_id, selected_lots, data, declaration_year):
        OperationService.check_declaration_year(declaration_year, data)
        OperationService.check_debited_entity(entity_id, data)
        OperationService.check_volumes(selected_lots, data)
        OperationService.check_objectives_compliance(request, selected_lots, data, entity_id, declaration_year)

    @staticmethod
    def check_debited_entity(entity_id, data):
        """
        Check if the debited entity is the same as entity_id passed in the request
        """
        if data["debited_entity"].id != entity_id:
            raise serializers.ValidationError({"debited_entity": OperationServiceErrors.ENTITY_ID_DO_NOT_MATCH_DEBITED_ID})

    @staticmethod
    def check_volumes(selected_lots, data):
        """
        Check if the selected lots exist and have enough volume to perform the operation
        """
        np_volumes, __, np_lot_ids, __, __ = TeneurService.prepare_data(data)

        # Normalize available and requested volumes to business precision.
        available_volumes = {int(lot_id): truncate(volume) for lot_id, volume in zip(np_lot_ids, np_volumes)}

        # Aggregate requested volumes per lot to correctly handle duplicate lot ids.
        requested_volumes = defaultdict(float)
        for lot in selected_lots:
            requested_volumes[lot["id"]] += truncate(lot["volume"])

        for lot_id, volume in requested_volumes.items():
            if lot_id not in available_volumes:
                raise serializers.ValidationError({"lot_id": [_(f"{lot_id}: Ce lot n'a pas de volume disponible")]})

            if available_volumes[lot_id] < volume:
                raise serializers.ValidationError(
                    {
                        "volume": [
                            _(
                                f"Lot id {lot_id} : Volume insuffisant pour ce lot (volume disponible: {available_volumes[lot_id]} L)"  # noqa: E501
                            )
                        ]
                    }
                )

    @staticmethod
    def bulk_check_volumes(entries):
        """
        Check that several requested operations combined have enough volume available.

        - entries: list of {"biofuel", "customs_category", "debited_entity", "selected_lots"} dicts.
        Entries sharing the same (biofuel, customs_category) are summed together before checking,
        since `check_volumes`'s availability lookup is scoped to that combination regardless
        of operation_type (e.g. a TENEUR group and a TRANSFERT group drawing from the same lots).
        """
        grouped: dict[tuple, dict] = {}
        for entry in entries:
            key = (entry["biofuel"].id, entry["customs_category"])
            group = grouped.setdefault(
                key,
                {
                    "biofuel": entry["biofuel"],
                    "customs_category": entry["customs_category"],
                    "debited_entity": entry["debited_entity"],
                    "lot_volumes": defaultdict(float),
                },
            )
            for lot in entry["selected_lots"]:
                group["lot_volumes"][lot["id"]] += lot["volume"]

        for group in grouped.values():
            selected_lots = [{"id": lot_id, "volume": volume} for lot_id, volume in group["lot_volumes"].items()]
            data = {
                "biofuel": group["biofuel"],
                "customs_category": group["customs_category"],
                "debited_entity": group["debited_entity"],
            }
            OperationService.check_volumes(selected_lots, data)

    @staticmethod
    def _check_teneur_target(request, entity_id, customs_category, teneur_to_add, declaration_year, bulk=False):
        """
        Check that adding `teneur_to_add` (in MJ) for the given customs category doesn't
        exceed the capped objective, based on the entity's already pending/declared teneur.
        """
        # 1. Get the target for the customs category
        target = ObjectiveService.calculate_target_for_specific_category(customs_category, request.entity.id)
        # Case for reach objective and no objective, no need to do this check compliance
        if target is None:
            return

        # 2. Calculate the balance for the requested customs category (all biofuels combined)
        request.GET = request.GET.copy()
        request.GET["customs_category"] = customs_category
        operations = OperationFilterForBalance(request.GET, queryset=Operation.objects.all(), request=request).qs

        balance = BalanceService.calculate_balance(
            operations,
            entity_id,
            "customs_category",
            "mj",
            declaration_year=declaration_year,
        )

        balance = list(balance.values())[0]  # keep the first (and only one) element

        # 3. Check if the futur teneur is below the target
        futur_teneur = (
            truncate(balance["pending_teneur"], 0) + truncate(balance["declared_teneur"], 0) + teneur_to_add
        )  # all in MJ

        target = truncate(target, 0)

        if futur_teneur > target:
            message = "La somme des teneurs" if bulk else "La teneur"
            raise serializers.ValidationError(
                {
                    "teneur": [
                        _(
                            f"{message} à créer ({teneur_to_add} MJ), pour la catégorie {customs_category}, dépasse l'objectif plafonné ({target} MJ)"  # noqa: E501
                        )
                    ]
                }
            )

    @staticmethod
    def check_objectives_compliance(request, selected_lots, data, entity_id, declaration_year):
        """
        Check if the TENEUR operation respects the capped objective for the customs category
        """
        if data["type"] != Operation.TENEUR:
            return

        # Convert the teneur to add from liters to MJ
        pci = data["biofuel"].pci_litre
        renewable_energy_share = data.get("renewable_energy_share", 1)
        teneur_to_add = truncate(
            sum(energy_mj(lot["volume"], pci, renewable_energy_share) for lot in selected_lots),
            0,
        )

        OperationService._check_teneur_target(request, entity_id, data["customs_category"], teneur_to_add, declaration_year)

    @staticmethod
    def bulk_check_objectives_compliance(request, entity_id, teneur_entries, declaration_year):
        """
        Check if several TENEUR operations combined respect the capped objective for their
        customs category.

        - teneur_entries: list of {"customs_category", "biofuel", "selected_lots"}
        dicts.
        """
        teneur_to_add_by_category = defaultdict(float)
        for entry in teneur_entries:
            pci = entry["biofuel"].pci_litre
            renewable_energy_share = entry.get("renewable_energy_share", 1)
            teneur_to_add_by_category[entry["customs_category"]] += truncate(
                sum(energy_mj(lot["volume"], pci, renewable_energy_share) for lot in entry["selected_lots"])
            )

        for customs_category, teneur_to_add in teneur_to_add_by_category.items():
            OperationService._check_teneur_target(
                request, entity_id, customs_category, teneur_to_add, declaration_year, bulk=True
            )

    @staticmethod
    def check_declaration_year(declaration_year, validated_data):
        if not declaration_year:
            raise serializers.ValidationError({"declaration_year": "Declaration year is required"})

        validated_data["declaration_year"] = declaration_year

    @staticmethod
    def define_operation_status(validated_data):
        """
        Define the operation status based on the entity type and operation type
        """
        auto_accepted_types = [
            Operation.INCORPORATION,
            Operation.MAC_BIO,
            Operation.LIVRAISON_DIRECTE,
            Operation.DEVALUATION,
        ]

        if validated_data["type"] in auto_accepted_types:
            validated_data["status"] = Operation.ACCEPTED
        elif validated_data.get("status") != Operation.DRAFT:
            validated_data["status"] = Operation.PENDING

    @staticmethod
    def create_operation_with_details(operation_data, details_data):
        """
        Create one operation and its related details.
        """
        operation = Operation.objects.create(**operation_data)

        OperationDetail.objects.bulk_create(
            [
                OperationDetail(
                    operation=operation,
                    lot_id=detail["lot_id"],
                    volume=truncate(detail["volume"]),
                    emission_rate_per_mj=detail["emission_rate_per_mj"],
                )
                for detail in details_data
            ]
        )

        return operation

    @staticmethod
    def build_details_data(lot_volumes, emissions_by_lot):
        """
        Build OperationDetail payloads from lot volumes and emission rates.
        """
        if hasattr(lot_volumes, "items"):
            lot_volume_items = lot_volumes.items()
        else:
            lot_volume_items = ((lot["id"], lot["volume"]) for lot in lot_volumes)

        return [
            {
                "lot_id": lot_id,
                "volume": truncate(volume, 2),
                "emission_rate_per_mj": emissions_by_lot.get(lot_id, 0),
            }
            for lot_id, volume in lot_volume_items
        ]

    @staticmethod
    @transaction.atomic
    def create_operations_from_lots(lots: list[CarbureLot]):
        """
        Create TIRUERT operations from CarbureLots.

        Groups lots by delivery_type, feedstock category, biofuel and depot,
        then creates one operation per group with associated details.
        """

        # Filter lots to keep only those that are valid for TIRUERT operations
        valid_lots = OperationService.filter_valid_lots(lots)
        valid_lots = OperationService.filter_fr_delivery_site(valid_lots)
        valid_lots = OperationService.remove_existing_lots(valid_lots)

        if not valid_lots:
            return []

        valid_lots = list(valid_lots)

        # Process EP2 lots, calculate ethanol 15° volumes for valid lots and convert EMAG lots
        valid_lots = OperationService.process_ep2_lots(valid_lots)
        OperationService.calculate_volume_ethanol_15(valid_lots)
        OperationService.convert_emag_lots(valid_lots)

        # Group validated_lots by delivery_type, feedstock, biofuel and depot
        lots_by_delivery_type = defaultdict(list)
        for lot in valid_lots:
            key = (lot.delivery_type, lot.feedstock.category, lot.biofuel.code, lot.carbure_delivery_site)
            lots_by_delivery_type[key].append(lot)

        matching_types = {
            CarbureLot.RFC: Operation.MAC_BIO,
            CarbureLot.BLENDING: Operation.INCORPORATION,
            CarbureLot.DIRECT: Operation.LIVRAISON_DIRECTE,
        }

        for key, lots in lots_by_delivery_type.items():
            credited_entity = lots[0].carbure_client or lots[0].carbure_supplier
            if not credited_entity:
                continue  # skip if no credited entity (should not happen for valid lots)

            operation_data = {
                "type": matching_types[key[0]],
                "status": Operation.VALIDATED,  # TODO: Set to PENDING when DGGDI validation will be implemented
                "customs_category": key[1],
                "biofuel": lots[0].biofuel,
                "credited_entity": credited_entity,
                "debited_entity": None,
                "from_depot": None,
                "to_depot": lots[0].carbure_delivery_site,
                "renewable_energy_share": lots[0].biofuel.renewable_energy_share,
                "durability_period": lots[0].period,
            }

            lot_volumes = {lot.id: lot.volume for lot in lots}
            emissions_by_lot = {lot.id: lot.ghg_total for lot in lots}
            details_data = OperationService.build_details_data(lot_volumes, emissions_by_lot)

            OperationService.create_operation_with_details(operation_data, details_data)

    @staticmethod
    def filter_valid_lots(lots: list[CarbureLot]):
        """
        Keep only lots compatible with TIRUERT.

        Valid lots must have:
        - lot_status in ["ACCEPTED", "FROZEN"]
        - delivery_type in [RFC, BLENDING, DIRECT]
        - if delivery_type is RFC, keep only some usage values or empty usage
        """
        DELIVERY_TYPES_ACCEPTED = [CarbureLot.BLENDING, CarbureLot.DIRECT]

        USAGE_WHITELIST = [
            CarbureLot.USAGE_ROAD,
            CarbureLot.USAGE_AGRICULTURE,
            CarbureLot.USAGE_CONSTRUCTION,
            CarbureLot.USAGE_MARITIME,
            CarbureLot.USAGE_INLAND_WATERWAY,
            CarbureLot.USAGE_RAIL,
        ]

        return lots.filter(lot_status__in=["ACCEPTED", "FROZEN"]).filter(
            Q(delivery_type=CarbureLot.RFC, usage__in=USAGE_WHITELIST)
            | Q(delivery_type=CarbureLot.RFC, usage="")
            | Q(delivery_type__in=DELIVERY_TYPES_ACCEPTED)
        )

    @staticmethod
    def filter_fr_delivery_site(lots: list[CarbureLot]):
        """
        Keep only lots with a delivery site in France, or with no delivery site.
        """
        return lots.filter(Q(carbure_delivery_site__country__code_pays="FR") | Q(carbure_delivery_site__isnull=True))

    @staticmethod
    def remove_existing_lots(lots: list[CarbureLot]):
        """
        Remove lots that already have an operation to avoid duplicates.
        """
        existing_lots = OperationDetail.objects.filter(lot__in=lots).values_list("lot_id").distinct()
        return lots.exclude(id__in=existing_lots)

    @staticmethod
    def process_ep2_lots(lots: list[CarbureLot]) -> list[CarbureLot]:
        """
        Split EP2 lots into two new lots (not saved to database).

        EP2 lots are split as:
        - 40% of volume → CONV category
        - 60% of volume → EP2AM category
        """
        result_lots = []

        for lot in lots:
            if lot.feedstock.code == "EP2":
                new_lot_conv = copy(lot)
                new_lot_conv.feedstock = copy(lot.feedstock)
                new_lot_conv.feedstock.category = MatierePremiere.CONV
                volume_decimal = Decimal(str(lot.volume))
                new_lot_conv.volume = truncate(float(volume_decimal * Decimal("0.4")))

                new_lot_ep2 = copy(lot)
                new_lot_ep2.feedstock = copy(lot.feedstock)
                new_lot_ep2.feedstock.category = MatierePremiere.EP2AM
                new_lot_ep2.volume = truncate(float(volume_decimal * Decimal("0.6")))

                result_lots.append(new_lot_conv)
                result_lots.append(new_lot_ep2)
            else:
                result_lots.append(lot)

        return result_lots

    @staticmethod
    def calculate_volume_ethanol_15(lots: list[CarbureLot]) -> None:
        """
        Calculate the corresponding total volume of ethanol 15° for each lot of ethanol 20°
        """
        conversion_factor = Decimal("0.995")

        for lot in lots:
            if lot.biofuel.code == "ETH":
                volume_decimal = Decimal(str(lot.volume))
                lot.volume = truncate(float(volume_decimal * conversion_factor))

    @staticmethod
    def convert_emag_lots(lots: list[CarbureLot]) -> dict[str, list[CarbureLot]]:
        """
        Lots with biofuel EMHV, EMHU, EMHA or B100 are converted to EMAG biofuel
        """
        emag = Biocarburant.objects.get(code="EMAG")
        for lot in lots:
            if lot.biofuel.code in ["EMHV", "EMHU", "EMHA", "B100"]:
                lot.biofuel = emag

    @staticmethod
    def define_sector(biofuel: Biocarburant) -> str:
        from saf.models.constants import SAF_BIOFUEL_TYPES

        if biofuel.compatible_essence:
            return Operation.ESSENCE
        elif biofuel.compatible_diesel:
            return Operation.GAZOLE
        elif biofuel.code in SAF_BIOFUEL_TYPES:
            return Operation.CARBUREACTEUR
        elif biofuel.compatible_gpl:
            return Operation.GPL_C
        return None
