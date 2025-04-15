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
    def calculate_energy_basis(mac_queryset, objective_queryset):
        """
        Calculate the energy basis (from fossil fuels mac), used for all objectives calculations
        """
        consideration_rates = ObjectiveService._get_consideration_rate_per_sector(objective_queryset)

        total_energy = mac_queryset.annotate(
            energy=models.F("volume")
            * models.F("fuel__fuel_category__pci_litre")
            * models.Case(
                *[
                    models.When(fuel__fuel_category__name=key, then=models.Value(value))
                    for key, value in consideration_rates.items()
                ],
                default=models.Value(1),
                output_field=models.FloatField(),
            )
        ).aggregate(total=models.Sum("energy"))["total"]

        return total_energy  # (MJ)

    @staticmethod
    def _get_consideration_rate_per_sector(objective_queryset, year=datetime.now().year):
        """
        Get consideration rate per sector
        """
        consideration_rates = objective_queryset.filter(
            type=Objective.SECTOR,
        ).values_list(
            "fuel_category__name",
            "consideration_rate",
        )

        return dict(consideration_rates)

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
        objectives = Objective.objects.filter(year=year)
        energy_basis = ObjectiveService.calculate_energy_basis(macs, objectives)

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
