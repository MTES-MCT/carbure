from datetime import datetime

from django.db import models

from tiruert.filters import OperationFilter
from tiruert.models import Objective, Operation
from tiruert.services.balance import BalanceService
from tiruert.services.teneur import GHG_REFERENCE_RED_II


class ObjectiveService:
    @staticmethod
    def calculate_energy_basis(mac_queryset, objective_queryset):
        """
        Calculate the energy basis (from fossiel fuels mac), used for all objectives calculations
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

    def calculate_objectives_per_categories(energy_basis, objective_queryset):
        """
        Get objective per categories
        """
        categories = objective_queryset.filter(type=Objective.BIOFUEL_CATEGORY)
        current_objectives = []

        for objective in categories:
            current_objectives.append(
                {
                    "customs_category": objective.customs_category,
                    "target_mj": energy_basis * objective.target,
                    "target_type": objective.target_type,
                }
            )
        return current_objectives

    @staticmethod
    def calculate_objective(balance, objective_queryset, energy_basis, objective_type):
        """
        Calculate the objective per category or sector
        """
        for key in balance:
            balance[key]["code"] = key
            balance[key]["objective"] = {
                "target_mj": None,
                "target_type": None,
            }

        objectives = objective_queryset.filter(type=objective_type)

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
                balance[key]["objective"] = {
                    "target_mj": energy_basis * objective.target,
                    "target_type": objective.target_type,
                }

        return list(balance.values())

    @staticmethod
    def calculate_global_objective(objective_queryset, energy_basis):
        """
        Calculate the global objective of CO2 emissions reduction
        """
        objectives = objective_queryset.filter(type=Objective.MAIN).values("target").first()
        return objectives["target"] * energy_basis

    @staticmethod
    def apply_ghg_conversion(value):
        return value * GHG_REFERENCE_RED_II / 1000000  # tCO2

    @staticmethod
    def get_balances_for_objectives_calculation(request, operations_with_date_from, entity_id):
        # Remove date_from filter from operations
        query_params = request.GET.copy()
        query_params.pop("date_from", None)
        all_operations = OperationFilter(data=query_params, queryset=Operation.objects.all(), request=request).qs

        # First get the whole balance (from forever), so with no date_from filter
        balance_per_category = BalanceService.calculate_balance(all_operations, entity_id, "customs_category", "mj")
        balance_per_sector = BalanceService.calculate_balance(all_operations, entity_id, "sector", "mj")

        # Then update the balance with quantity and teneur details for requested dates
        balance_per_category = BalanceService.calculate_balance(
            operations_with_date_from, entity_id, "customs_category", "mj", balance_per_category, update_balance=True
        )
        balance_per_sector = BalanceService.calculate_balance(
            operations_with_date_from, entity_id, "sector", "mj", balance_per_sector, update_balance=True
        )

        return balance_per_category, balance_per_sector
