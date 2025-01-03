from collections import defaultdict

import numpy as np
import scipy.optimize
from django.db.models import Q

from tiruert.models import Operation


class BalanceService:
    @staticmethod
    def calculate_balance(operations, entity_id, group_by):
        """
        Keep only PENDING and ACCEPTED operations
        Group by sector, customs_category and biofuel (and lot if needed)
        Sum volume and ghg: credit when entity is credited, debit when entity is debited
        """

        balance = defaultdict(
            lambda: {
                "sector": None,
                "customs_category": None,
                "biofuel": None,
                "volume": {"credit": 0, "debit": 0},
                "ghg": {"credit": 0, "debit": 0},
                "pending": 0,
            }
        )

        operations = operations.filter(status__in=[Operation.PENDING, Operation.ACCEPTED])

        for operation in operations:
            for detail in operation.details.all():
                key = (operation.sector, operation.customs_category, operation.biofuel.code)

                if group_by == "lot":
                    key = key + (detail.lot.id,)

                if group_by == "sector":
                    key = operation.sector

                balance[key]["sector"] = operation.sector
                if group_by != "sector":
                    balance[key]["customs_category"] = operation.customs_category
                    balance[key]["biofuel"] = operation.biofuel.code

                if operation.is_credit(entity_id):
                    balance[key]["volume"]["credit"] += detail.volume
                    balance[key]["ghg"]["credit"] += detail.saved_ghg
                else:
                    balance[key]["volume"]["debit"] += detail.volume
                    balance[key]["ghg"]["debit"] += detail.saved_ghg

            if group_by != "lot" and operation.status == Operation.PENDING:
                balance[key]["pending"] += 1

        return balance

    @staticmethod
    def calculate_initial_balance(balance, entity_id, until_date, group_by):
        """
        Calculate initial balances for the given entity until the given date
        and add them to the balance dict
        """
        operations = Operation.objects.filter(
            created_at__lt=until_date,
            status__in=[Operation.PENDING, Operation.ACCEPTED],
        ).filter((Q(credited_entity_id=2) | Q(debited_entity_id=2)))

        initial_balances = defaultdict(int)

        for operation in operations:
            key = (
                operation.sector
                if group_by == "sector"
                else (operation.sector, operation.customs_category, operation.biofuel.code)
            )

            # Handle the case where there are operations for a specific biofuel before the requested date, but
            # no operations after
            # In this case, the key won't be in the balance dict
            if key not in balance:
                balance[key] = {
                    "volume": {"credit": 0, "debit": 0},
                    "ghg": {"credit": 0, "debit": 0},
                    "pending": 0,
                    "sector": operation.sector,
                }
                if group_by != "sector":
                    balance[key]["customs_category"] = operation.customs_category
                    balance[key]["biofuel"] = operation.biofuel.code

            for detail in operation.details.all():
                initial_balances[key] += detail.volume if operation.is_credit(entity_id) else -detail.volume

        for key in balance:
            balance[key]["initial_balance"] = initial_balances[key]

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
