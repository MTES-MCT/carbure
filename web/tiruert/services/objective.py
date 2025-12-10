from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware

from tiruert.models import MacFossilFuel, Objective
from tiruert.models.elec_operation import ElecOperation
from tiruert.services.balance import BalanceService
from tiruert.services.elec_balance import ElecBalanceService
from tiruert.services.teneur import GHG_REFERENCE_RED_II


class ObjectiveService:
    @staticmethod
    def calculate_energy_basis(mac_queryset, year=None):
        """
        Calculate the energy basis (from fossil fuels mac), used for all objectives calculations
        """
        if year is None:
            year = timezone.now().year

        total_energy = mac_queryset.annotate(
            energy=models.F("volume")
            * models.F("fuel__fuel_category__pci_litre")
            * models.Case(
                models.When(
                    fuel__fuel_category__consideration_rates__year=year,
                    then=models.F("fuel__fuel_category__consideration_rates__consideration_rate"),
                ),
                default=1,
                output_field=models.FloatField(),
            )
        ).aggregate(total=models.Sum("energy"))["total"]

        return total_energy  # (MJ)

    @staticmethod
    def calculate_objectives_and_penalties(balance, objective_queryset, energy_basis, objective_type):
        """
        Calculate the objective per category or sector
        """
        for key in balance:
            balance[key]["code"] = key
            balance[key]["objective"] = {
                "target_mj": None,
                "target_type": None,
                "penalty": None,
                "target_percent": None,
            }

        objectives = objective_queryset.filter(type=objective_type)
        if not objectives.exists():
            return list(balance.values())

        for objective in objectives:
            if objective_type == Objective.BIOFUEL_CATEGORY:
                key = objective.customs_category
            elif objective_type == Objective.SECTOR:
                key = objective.fuel_category.name.upper()
            else:
                continue

            if key not in balance:
                continue
            else:
                target = ObjectiveService._calculate_target_for_objective(objective.target, energy_basis)
                penalty_amout = ObjectiveService._calcule_penalty(
                    objective.penalty,
                    balance[key]["pending_teneur"] + balance[key]["declared_teneur"],
                    target,
                )

                balance[key]["objective"] = {
                    "target_mj": target,
                    "target_type": objective.target_type,
                    "penalty": penalty_amout,
                    "target_percent": objective.target,
                }

        return list(balance.values())

    @staticmethod
    def get_elec_category(elec_operations, entity_id, date_from):
        elec_category = ElecBalanceService.calculate_balance(elec_operations, entity_id, date_from)

        elec_category["code"] = ElecOperation.SECTOR
        elec_category["unit"] = "mj"

        elec_category["objective"] = {
            "target_mj": None,
            "target_type": None,
            "penalty": None,
            "target_percent": None,
        }

        return elec_category

    @staticmethod
    def get_global_objective_and_penalty(objective_queryset, energy_basis):
        """
        Calculate the global objective of CO2 emissions reduction
        """
        objective = objective_queryset.filter(type=Objective.MAIN).values("target", "penalty").first()
        target = ObjectiveService._calculate_target_for_objective(objective["target"], energy_basis) if objective else 0
        penalty = objective["penalty"] if objective else 0
        target_percent = objective["target"] if objective else 0
        return target, penalty, target_percent

    @staticmethod
    def apply_ghg_conversion(value):
        return value * GHG_REFERENCE_RED_II / 1000000  # tCO2

    @staticmethod
    def apply_elec_ghg_conversion(value):
        return value * ElecOperation.EMISSION_RATE_PER_MJ / 1e6  # tCO2

    @staticmethod
    def calculate_global_objective(objective_per_sector, elec_category, objectives, energy_basis):
        """
        Calculate the global objective by aggregating sector balances and applying GHG conversions.

        Returns:
            dict: Global objective with available_balance, target, pending_teneur, declared_teneur,
                  unit, target_percent, energy_basis, and penalty.
        """
        # Get global objective target and penalty from objectives
        global_objective_target, global_objective_penalty, global_objective_target_percent = (
            ObjectiveService.get_global_objective_and_penalty(objectives, energy_basis)
        )

        # Sum sector values
        available_balance_sum = sum(sector["available_balance"] for sector in objective_per_sector)
        pending_teneur_sum = sum(sector["pending_teneur"] for sector in objective_per_sector)
        declared_teneur_sum = sum(sector["declared_teneur"] for sector in objective_per_sector)

        # Apply GHG conversions for biofuel
        biofuel_available_balance = ObjectiveService.apply_ghg_conversion(available_balance_sum)
        biofuel_pending_teneur = ObjectiveService.apply_ghg_conversion(pending_teneur_sum)
        biofuel_declared_teneur = ObjectiveService.apply_ghg_conversion(declared_teneur_sum)

        # Apply GHG conversions for elec
        elec_available_balance = ObjectiveService.apply_elec_ghg_conversion(elec_category["available_balance"])
        elec_pending_teneur = ObjectiveService.apply_elec_ghg_conversion(elec_category["pending_teneur"])
        elec_declared_teneur = ObjectiveService.apply_elec_ghg_conversion(elec_category["declared_teneur"])

        # Build global objective
        global_objective = {
            "available_balance": biofuel_available_balance + elec_available_balance,
            "target": ObjectiveService.apply_ghg_conversion(global_objective_target),
            "pending_teneur": biofuel_pending_teneur + elec_pending_teneur,
            "declared_teneur": biofuel_declared_teneur + elec_declared_teneur,
            "unit": "tCO2",
            "target_percent": global_objective_target_percent,
            "energy_basis": energy_basis,
        }

        # Calculate penalty
        penalty = ObjectiveService._calcule_penalty(
            global_objective_penalty,
            global_objective["pending_teneur"] + global_objective["declared_teneur"],
            global_objective["target"],
            tCO2=True,
        )
        global_objective["penalty"] = penalty

        return global_objective

    @staticmethod
    def aggregate_objectives(objectives_list: list[dict]) -> dict:
        """
        Aggregate a list of objectives results into a single aggregated result.

        Args:
            objectives_list: List of objectives dicts with keys 'main', 'sectors', 'categories'

        Returns:
            Aggregated objectives dict with same structure
        """
        if not objectives_list:
            return None

        # Initialize aggregated structures
        aggregated_main = {
            "available_balance": 0,
            "target": 0,
            "pending_teneur": 0,
            "declared_teneur": 0,
            "unit": "tCO2",
            "target_percent": None,
            "penalty": 0,
            "energy_basis": 0,
        }
        aggregated_sectors = {}
        aggregated_categories = {}

        # Keys to sum in main
        main_sum_keys = ["available_balance", "target", "pending_teneur", "declared_teneur", "penalty", "energy_basis"]
        # Keys to sum in sectors/categories
        balance_sum_keys = ["pending_teneur", "declared_teneur", "available_balance"]
        objective_sum_keys = ["target_mj", "penalty"]

        for objectives in objectives_list:
            # Aggregate main
            for key in main_sum_keys:
                if key in objectives["main"]:
                    aggregated_main[key] += objectives["main"][key]

            # Take first non-None target_percent
            if aggregated_main["target_percent"] is None and objectives["main"].get("target_percent") is not None:
                aggregated_main["target_percent"] = objectives["main"]["target_percent"]

            # Aggregate sectors
            ObjectiveService._aggregate_items(
                objectives["sectors"], aggregated_sectors, balance_sum_keys, objective_sum_keys
            )

            # Aggregate categories
            ObjectiveService._aggregate_items(
                objectives["categories"], aggregated_categories, balance_sum_keys, objective_sum_keys
            )

        return {
            "main": aggregated_main,
            "sectors": list(aggregated_sectors.values()),
            "categories": list(aggregated_categories.values()),
        }

    @staticmethod
    def _aggregate_items(items: list[dict], aggregated: dict, balance_keys: list, objective_keys: list):
        """
        Aggregate a list of sector or category items into the aggregated dict.
        """
        for item in items:
            code = item["code"]
            if code not in aggregated:
                aggregated[code] = item.copy()
                if "objective" in item and item["objective"]:
                    aggregated[code]["objective"] = item["objective"].copy()
            else:
                # Sum balance keys
                for key in balance_keys:
                    if key in item:
                        aggregated[code][key] += item[key]

                # Sum objective keys
                if "objective" in item and item["objective"]:
                    for key in objective_keys:
                        if item["objective"].get(key) is not None:
                            if aggregated[code]["objective"].get(key) is None:
                                aggregated[code]["objective"][key] = 0
                            aggregated[code]["objective"][key] += item["objective"][key]

    @staticmethod
    def get_balances_for_objectives_calculation(operations, entity_id, date_from):
        date_from = make_aware(datetime.strptime(date_from, "%Y-%m-%d"))

        balance_per_category = BalanceService.calculate_balance(operations, entity_id, "customs_category", "mj", date_from)
        balance_per_sector = BalanceService.calculate_balance(operations, entity_id, "sector", "mj", date_from)

        return balance_per_category, balance_per_sector

    @staticmethod
    def _get_capped_objectives(year):
        """
        Get capped objectives for the given year
        Only for 'customs_category' objectives ('sector' and 'main' not handled for now)
        """
        return Objective.objects.filter(year=year, target_type=Objective.CAP, type=Objective.BIOFUEL_CATEGORY)

    @staticmethod
    def _calculate_target_for_objective(target, energy_basis):
        """
        Calculate the target for the given objective
        """
        return energy_basis * target  # MJ

    @staticmethod
    def calculate_target_for_specific_category(customs_category, entity_id):
        """
        Calculate the objective target for a specific customs category
        """
        # 1. Get the capped objective for the given year and customs category
        year = timezone.now().year
        capped_objectives = ObjectiveService._get_capped_objectives(year)
        objective = capped_objectives.filter(customs_category=customs_category).first()
        if not objective:
            return None

        # 2. Calculate "assiette" used for objectives calculations
        macs = MacFossilFuel.objects.filter(operator_id=entity_id, year=year)
        energy_basis = ObjectiveService.calculate_energy_basis(macs, year)
        if not energy_basis:
            return None

        # 3. Calculate the target objective for the customs category
        target = ObjectiveService._calculate_target_for_objective(objective.target, energy_basis)  # MJ
        return target

    @staticmethod
    def _calcule_penalty(penalty, teneur, target, tCO2=False):
        """
        Calculate the penalty for the given objective
        If tCO2 is True, the penalty is in c€/tCO2
        - teneur is in tCO2
        - target is in tCO2
        If tCO2 is False, the penalty is in c€/GJ
        - teneur is in MJ (need to convert to GJ)
        - target is in MJ (need to convert to GJ)
        """
        if not penalty or not target:
            return 0

        if teneur < target:
            diff = target - teneur
            diff = diff / 1000 if not tCO2 else diff
            penalty_amount = diff * penalty
            return penalty_amount
        else:
            return 0
