import numpy as np
import scipy.optimize
from django.db.models import Q

from tiruert.models import Operation
from tiruert.services.balance import BalanceService


class TeneurServiceErrors:
    NO_SUITABLE_LOTS_FOUND = "NO_SUITABLE_LOTS_FOUND"
    INSUFFICIENT_INPUT_VOLUME = "INSUFFICIENT_INPUT_VOLUME"


class TeneurService:
    @staticmethod
    def optimize_biofuel_blending(batches_volumes, batches_emissions, target_volume, target_emission):
        """Prototype for biofuel batches optimal blending.

        The coefficients of the objective function `c` are:
        - The batches respective emissions levels.
        - The user-input emission "target" as the last element.

        By setting the decision variables vector x last value to 1, the scalar product <c, x> is
        the difference between the emissions after blending and the user-input target emission.
        Minimizing this scalar product yields the intended volumes vector.

        We set the other constraints accordingly to the following:
        - The sum of the available volumes must be greater than the target volume.
        - x's elements must be positive, and their sum must be equal to the target volume.
        """

        # REFERENCE_EMISSION = 67.5

        # Target definition
        # target_change = -0.10  # as a fraction of the reference emissions in [0; 1]
        # target_emission = (1 + target_change) * REFERENCE_EMISSION

        error = None

        if batches_volumes.sum() < target_volume:
            error = TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME
            return None, None, error

        # Optimization objective
        c = np.concat((-1 / target_volume * batches_emissions, [target_emission]))

        # Constraints
        A = np.array([c, [1 for _ in batches_volumes] + [0]])
        b_l = [0, target_volume]
        b_u = [np.inf, target_volume]

        res = scipy.optimize.milp(
            c,
            integrality=0,
            bounds=scipy.optimize.Bounds(lb=[0 for _ in batches_volumes] + [1], ub=batches_volumes.tolist() + [1]),
            constraints=(A, b_l, b_u),
        )

        result_array = res.x

        # retourner res.fun + target_emission

        if not res.success:
            error = TeneurServiceErrors.NO_SUITABLE_LOTS_FOUND
            return None, res.fun, error

        # Find the indices of the nonzero elements
        nonzero_indices = np.nonzero(result_array[:-1])[0]  # [:-1] excludes the last element, always 1

        # Create a dictionary of selected batches with their respective index and volume
        selected_batches_volumes = {idx: result_array[idx] for idx in nonzero_indices}

        return selected_batches_volumes, res.fun, error

    @staticmethod
    def prepare_data_and_optimize(entity_id, data):
        volumes, emissions, lot_ids = TeneurService.prepare_data(entity_id, data)

        selected_lots, fun, error = TeneurService.optimize_biofuel_blending(
            volumes,
            emissions,
            data.pop("target_volume"),
            data.pop("target_emission"),
        )

        return selected_lots, lot_ids, emissions, fun, error

    @staticmethod
    def get_min_and_max_emissions(entity_id, data):
        """
        Compute minimum and maximum feasible mix emissions.
        Return emission rates per MJ
        """
        volumes, emissions, lot_ids = TeneurService.prepare_data(entity_id, data)
        error = None

        if volumes.sum() < data["target_volume"]:
            error = TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME
            return None, None, error

        emissions_sorter = np.argsort(emissions)
        emissions_inv_sorter = emissions_sorter[::-1]
        thresh_min = (data["target_volume"] < volumes[emissions_sorter].cumsum()).argmax()
        thresh_max = (data["target_volume"] < volumes[emissions_inv_sorter].cumsum()).argmax()
        blend_emission_min = (
            np.dot(
                volumes[emissions_sorter][:thresh_min],
                emissions[emissions_sorter][:thresh_min],
            )
            + (
                (data["target_volume"] - volumes[emissions_sorter][:thresh_min].sum())
                * emissions[emissions_sorter][thresh_min]
            )
        ) / data["target_volume"]

        blend_emission_max = (
            np.dot(
                volumes[emissions_inv_sorter][:thresh_max],
                emissions[emissions_inv_sorter][:thresh_max],
            )
            + (
                (data["target_volume"] - volumes[emissions_inv_sorter][:thresh_max].sum())
                * emissions[emissions_inv_sorter][thresh_max]
            )
        ) / data["target_volume"]

        return blend_emission_min, blend_emission_max, error

    @staticmethod
    def prepare_data(entity_id, data):
        """
        Prepare data for optimization
        """
        operations = (
            Operation.objects.filter(
                biofuel=data["biofuel"],
                customs_category=data["customs_category"],
                # created_at__gte=data["date_from"],
            )
            .filter((Q(credited_entity=data["debited_entity"]) | Q(debited_entity=data["debited_entity"])))
            .distinct()
        )

        # Calculate balance of debited entity
        balance = BalanceService.calculate_balance(operations, entity_id, "lot")

        # Rearrange balance in an array of all volumes sums and an array of all ghg sums
        # For each we have something like:
        # array([30.52876597, 42.1162736 , 30.07384206, 25.05628985, 85.52717505])
        volumes, emissions, lot_ids = np.array([]), np.array([]), np.array([])

        for key, value in balance.items():
            sector, customs_cat, biofuel, lot_id = key
            volumes = np.append(volumes, value["volume"]["credit"] - value["volume"]["debit"])
            emissions = np.append(emissions, value["emission_rate_per_mj"])
            lot_ids = np.append(lot_ids, lot_id)

        return volumes, emissions, lot_ids
