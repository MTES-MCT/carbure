from datetime import datetime

from tiruert.models import Objective


class ObjectiveService:
    @staticmethod
    def objectives_settings(year=datetime.now().year):
        """
        Get the objectives settings
        """
        return Objective.objects.filter(year=year)

    @staticmethod
    def calculate_energy_basis(mac_queryset, objective_queryset):
        """
        Calculate the energy basis (from fossiel fuels mac), used for all objectives calculations
        """
        consideration_rate_per_sector = ObjectiveService._get_consideration_rate_per_sector(objective_queryset)

        total_energy = sum(
            [
                mac.volume * mac.fuel.fuel_category.pci_litre * consideration_rate_per_sector[mac.fuel.fuel_category.name]
                for mac in mac_queryset
            ]
        )
        total_energy_tonnes = total_energy / 1000  # tCO2
        return total_energy_tonnes

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
