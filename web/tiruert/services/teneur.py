from typing import Optional

import numpy as np
import numpy.typing as npt
import scipy.optimize
from django.db.models import Q

from tiruert.models import Operation
from tiruert.services.balance import BalanceService


class TeneurServiceErrors:
    NO_SUITABLE_LOTS_FOUND = "NO_SUITABLE_LOTS_FOUND"
    INSUFFICIENT_INPUT_VOLUME = "INSUFFICIENT_INPUT_VOLUME"
    ENFORCED_VOLUMES_TOO_HIGH = "ENFORCED_VOLUMES_TOO_HIGH"
    INCOHERENT_ENFORCED_VOLUMES_WITH_MAX_N_BATCHES = "INCOHERENT_ENFORCED_VOLUMES_WITH_MAX_N_BATCHES"


class TeneurService:
    @staticmethod
    def optimize_biofuel_blending(
        batches_volumes: npt.NDArray[np.float64],
        batches_emissions: npt.NDArray[np.float64],
        target_volume: float,
        target_emission: float,
        enforced_volumes: Optional[npt.NDArray[np.float64]] = None,
        max_n_batches: Optional[int] = None,
    ) -> scipy.optimize.OptimizeResult:
        r"""Compute optimal batches volumes using linear programming.

        The coefficients of `c` define the objective. It contains, in order:
        - The batches emissions levels, divided by the target volume.
        - Zeroes, corresponding to the batch inclusion boolean flags.
        - The emission per energy "target" as the last element.

        We set the linear constraints accordingly to the following:
        - `b_l <= A @ x <= b_u` constraints (in order of appearance inside the `A` matrix):
        - Mix emissions should be less or equal than target.
        - The sum of the extracted volumes should equal target volume.
        - The number of batches with non-zero extracted volume is less or equal than
            `max_batches_constraint`.
        - `x_bounds`:
        - `x`'s elements must lie between zero and available volume for each batch.
        - The last coefficient is forced to 1 so that <c, x> defines the objective.

        By forcing the decision variables vector x last value to 1, the scalar product
        :math:`c^T \dot x` is the difference between the "mix emissions" and the user-input
        target emission. Minimizing this scalar product yields the intended volumes vector.

        Args:
            batches_volumes: The batches volumes (in L).
            batches_emissions: The batches emission rates (in CO2/MJ)
            target_volume: The total required volume to extract from the batches.
            target_emission: A target emission rate.
            enforced_volumes (opt): An array with the same size as `batches_volumes`. It
            contains values that will be forced into the response vector for each
            corresponding batch.
            max_n_batches (opt): If set, the number of non-zero volumes will be restricted
            to be less or equal than this value.

        Returns:
            A scipy optimize result object. `res.x[:len(batches_volumes)]` contains the
            computed volumes.

        """

        # Sanity checks on inputs
        if batches_volumes.sum() < target_volume:
            raise ValueError(TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME)

        if enforced_volumes is not None:
            if (enforced_volumes > batches_volumes).any():
                raise ValueError(TeneurServiceErrors.ENFORCED_VOLUMES_TOO_HIGH)
        else:
            enforced_volumes = np.zeros_like(batches_volumes)

        if max_n_batches is not None:
            if max_n_batches < (enforced_volumes != 0).sum():
                raise ValueError(TeneurServiceErrors.INCOHERENT_ENFORCED_VOLUMES_WITH_MAX_N_BATCHES)
        else:
            max_n_batches = len(batches_volumes)

        # Optimization objective
        c = np.concat(
            (
                -1 / target_volume * batches_emissions,
                [0.0 for _ in batches_volumes],
                [target_emission],
            )
        )
        # Linear inequality constraints
        A = np.vstack(
            (
                c,
                np.array([1 for _ in batches_volumes] + [0 for _ in batches_volumes] + [0]),
                np.array([0 for _ in batches_volumes] + [1 for _ in batches_volumes] + [0]),
                np.hstack(
                    (
                        np.diag(-1.0 * np.ones(len(batches_volumes))),
                        batches_volumes.max() * np.identity(len(batches_volumes)),
                        np.zeros((len(batches_volumes), 1)),
                    )
                ),
            )
        )
        b_l = [0.0, target_volume, 0] + [0.0 for _ in batches_volumes]
        b_u = [np.inf, target_volume, max_n_batches] + [np.inf for _ in batches_volumes]

        # Response vector constraints
        enforced_mask = enforced_volumes != 0
        vol_lb = np.where(enforced_mask, enforced_volumes, np.zeros_like(batches_volumes))
        vol_ub = np.where(enforced_mask, enforced_volumes, batches_volumes)

        x_bounds = scipy.optimize.Bounds(
            lb=np.concatenate((vol_lb, [0 for _ in batches_volumes], [1])),
            ub=np.concatenate((vol_ub, [1 for _ in batches_volumes], [1])),
        )

        res = scipy.optimize.milp(
            c,
            # The volumes need not be integers, but the coefficient associated with the max
            # number of batches are binary variables, so we set them to integers inside
            # [0;1]
            integrality=[0 for _ in batches_volumes] + [1 for _ in batches_volumes] + [0],
            bounds=x_bounds,
            constraints=(A, b_l, b_u),
        )

        result_array = res.x

        if not res.success:
            raise ValueError(TeneurServiceErrors.NO_SUITABLE_LOTS_FOUND)

        # Find the indices of the nonzero elements
        nonzero_indices = np.nonzero(result_array[0 : len(batches_volumes)])[0]

        # Create a dictionary of selected batches with their respective index and volume
        selected_batches_volumes = {idx: result_array[idx] for idx in nonzero_indices}

        return selected_batches_volumes, res.fun

    def emission_bounds(
        batches_volumes: npt.NDArray, batches_emissions: npt.NDArray, target_volume: float
    ) -> tuple[float, float]:
        """Computes emission rate bounds for a set of batches.

        Args:
            batches_volumes: The batches volumes (in L).
            batches_emissions: The batches emission rates (in CO2/MJ)
            target_volume: The total required volume to extract from the batches.

        Returns:
            A couple of (min_emissions_rate, max_emissions_rate)

        """

        # Sanity checks on inputs
        if batches_volumes.sum() < target_volume:
            raise ValueError(TeneurServiceErrors.INSUFFICIENT_INPUT_VOLUME)

        emissions_sorter = np.argsort(batches_emissions)
        emissions_inv_sorter = emissions_sorter[::-1]
        thresh_min = (target_volume < batches_volumes[emissions_sorter].cumsum()).argmax()
        thresh_max = (target_volume < batches_volumes[emissions_inv_sorter].cumsum()).argmax()

        min_emissions_rate = (
            np.dot(
                batches_volumes[emissions_sorter][:thresh_min],
                batches_emissions[emissions_sorter][:thresh_min],
            )
            + (
                (target_volume - batches_volumes[emissions_sorter][:thresh_min].sum())
                * batches_emissions[emissions_sorter][thresh_min]
            )
        ) / target_volume
        max_emissions_rate = (
            np.dot(
                batches_volumes[emissions_inv_sorter][:thresh_max],
                batches_emissions[emissions_inv_sorter][:thresh_max],
            )
            + (
                (target_volume - batches_volumes[emissions_inv_sorter][:thresh_max].sum())
                * batches_emissions[emissions_inv_sorter][thresh_max]
            )
        ) / target_volume
        return min_emissions_rate, max_emissions_rate

    @staticmethod
    def prepare_data_and_optimize(entity_id, data):
        volumes, emissions, lot_ids, enforced_volumes = TeneurService.prepare_data(entity_id, data)

        selected_lots, fun = TeneurService.optimize_biofuel_blending(
            volumes,
            emissions,
            data.pop("target_volume"),
            data.pop("target_emission"),
            enforced_volumes,
            data.pop("max_n_batches") if "max_n_batches" in data else None,
        )

        return selected_lots, lot_ids, emissions, fun

    @staticmethod
    def get_min_and_max_emissions(entity_id, data):
        """
        Compute minimum and maximum feasible mix emissions.
        Return emission rates per MJ
        """
        volumes, emissions, lot_ids, enforced_volumes = TeneurService.prepare_data(entity_id, data)

        min_emissions_rate, max_emissions_rate = TeneurService.emission_bounds(
            volumes,
            emissions,
            data["target_volume"],
        )

        return min_emissions_rate, max_emissions_rate

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
        enforced_volumes = np.array([]) if "enforced_volumes" in data else None

        for key, value in balance.items():
            sector, customs_cat, biofuel, lot_id = key
            volumes = np.append(volumes, value["volume"]["credit"] - value["volume"]["debit"])
            emissions = np.append(emissions, value["emission_rate_per_mj"])
            lot_ids = np.append(lot_ids, lot_id)

            if enforced_volumes is not None:
                volume = value["volume"]["credit"] - value["volume"]["debit"] if lot_id in data["enforced_volumes"] else 0
                enforced_volumes = np.append(enforced_volumes, volume)

        return volumes, emissions, lot_ids, enforced_volumes
