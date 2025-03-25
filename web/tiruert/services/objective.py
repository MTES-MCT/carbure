from datetime import datetime

from django.db import models
from django.utils.timezone import make_aware

from tiruert.models import Objective
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
        objective = objective_queryset.filter(type=Objective.MAIN).values("target").first()

        return objective["target"] * energy_basis if objective else 0

    @staticmethod
    def apply_ghg_conversion(value):
        return value * GHG_REFERENCE_RED_II / 1000000  # tCO2

    @staticmethod
    def get_balances_for_objectives_calculation(request, operations, entity_id, date_from):
        # First get the whole balance (from forever), so with no date_from filter
        balance_per_category = BalanceService.calculate_balance(operations, entity_id, "customs_category", "mj")
        balance_per_sector = BalanceService.calculate_balance(operations, entity_id, "sector", "mj")

        # Then update the balance with quantity and teneur details for requested dates
        date_from = make_aware(datetime.strptime(date_from, "%Y-%m-%d"))
        operations_with_date_from = operations.filter(created_at__gte=date_from)
        balance_per_category = BalanceService.calculate_balance(
            operations_with_date_from, entity_id, "customs_category", "mj", balance_per_category, update_balance=True
        )
        balance_per_sector = BalanceService.calculate_balance(
            operations_with_date_from, entity_id, "sector", "mj", balance_per_sector, update_balance=True
        )

        return balance_per_category, balance_per_sector
