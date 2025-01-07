import numpy as np
import scipy.optimize
from django.db.models import Q

from tiruert.models import Operation
from tiruert.services.balance import BalanceService


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

        if batches_volumes.sum() < target_volume:
            raise ValueError("Insufficient input volumes!")

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
            return False

        # Find the indices of the nonzero elements
        nonzero_indices = np.nonzero(result_array[:-1])[0]  # [:-1] excludes the last element, always 1

        # Create a dictionary of selected batches with their respective index and volume
        selected_batches_volumes = {idx: result_array[idx] for idx in nonzero_indices}

        return selected_batches_volumes, res.fun

    @staticmethod
    def prepare_data_and_optimize(entity_id, data):
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
        group_by = "lot"
        balance = BalanceService.calculate_balance(operations, entity_id, group_by)

        # Rearrange balance in an array of all volumes sums and an array of all ghg sums
        # For each we have something like:
        # array([30.52876597, 42.1162736 , 30.07384206, 25.05628985, 85.52717505])
        volumes, emissions, lot_ids = np.array([]), np.array([]), np.array([])

        for key, value in balance.items():
            sector, customs_cat, biofuel, lot_id = key
            volumes = np.append(volumes, value["volume"]["credit"] - value["volume"]["debit"])
            emissions = np.append(emissions, value["ghg"]["credit"] - value["ghg"]["debit"])
            lot_ids = np.append(lot_ids, lot_id)

        # print(volumes)
        # print(emissions)
        # print(lot_ids)

        selected_lots, fun = TeneurService.optimize_biofuel_blending(
            volumes,
            emissions,
            data.pop("target_volume"),
            data.pop("target_emission"),
        )

        return selected_lots, lot_ids, emissions, fun
