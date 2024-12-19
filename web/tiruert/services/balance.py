from collections import defaultdict

import numpy as np
import scipy.optimize

from tiruert.models import Operation


class BalanceService:
    @staticmethod
    def calculate_balance(operations, entity_id, by_lot=False):
        # Keep only PENDING and ACCEPTED operations
        # Group by customs_category and biofuel
        # Sum volume and ghg: credit when entity is credited, debit when entity is debited
        balance = defaultdict(lambda: {"volume": {"credit": 0, "debit": 0}, "ghg": {"credit": 0, "debit": 0}, "pending": 0})
        for operation in operations.filter(status__in=[Operation.PENDING, Operation.ACCEPTED]):
            grouped_by = (operation.customs_category, operation.biofuel)
            for detail in operation.details.all():
                key = grouped_by
                if by_lot:
                    key = grouped_by + (detail.lot.id,)

                # Get the volume balance for this key
                volume_balance = balance[key]["volume"]

                # Get the ghg balance for this key
                ghg_balance = balance[key]["ghg"]

                if operation.is_credit(entity_id):
                    # Add the volume of the detail to the volume balance
                    volume_balance["credit"] += detail.volume
                    # Add the saved_ghg of the detail to the ghg balance
                    ghg_balance["credit"] += detail.saved_ghg
                else:
                    volume_balance["debit"] += detail.volume
                    ghg_balance["debit"] += detail.saved_ghg

            if not by_lot and operation.PENDING:
                balance[grouped_by]["pending"] += 1

        return balance

    @staticmethod
    def calculate_initial_balance(balance, entity_id, until_date):
        operations = Operation.objects.filter(created_at__lt=until_date)

        initial_balances = {}
        for operation in operations.filter(status__in=[Operation.PENDING, Operation.ACCEPTED]):
            key = (operation.customs_category, operation.biofuel)
            if key not in initial_balances:
                initial_balances[key] = 0

            for detail in operation.details.all():
                if operation.is_credit(entity_id):
                    initial_balances[key] += detail.volume
                else:
                    initial_balances[key] -= detail.volume

        for key, _ in initial_balances.items():
            if not balance.get(key):
                balance[key] = {"volume": {"credit": 0, "debit": 0}, "ghg": {"credit": 0, "debit": 0}, "pending": 0}

        for key, item in balance.items():
            item["initial_balance"] = initial_balances.get(key, 0)

        return balance

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

        if not res.success:
            return False

        # Find the indices of the nonzero elements
        nonzero_indices = np.nonzero(result_array[:-1])[0]  # [:-1] excludes the last element, always 1

        # Create a dictionary of selected batches with their respective index and volume
        selected_batches_volumes = {idx: result_array[idx] for idx in nonzero_indices}

        return selected_batches_volumes
