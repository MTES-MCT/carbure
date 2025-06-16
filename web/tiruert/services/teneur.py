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


GHG_REFERENCE_RED_II = 94  # gCO2/MJ


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
                np.array(
                    [1 for _ in batches_volumes] + [0 for _ in batches_volumes] + [0],
                ),
                np.array(
                    [0 for _ in batches_volumes] + [1 for _ in batches_volumes] + [0],
                ),
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

    @staticmethod
    def emission_bounds(
        batches_volumes: npt.NDArray,
        batches_emissions: npt.NDArray,
        target_volume: float,
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

        # Handle case where the target volume is exactly the sum of the batches volumes
        if target_volume == batches_volumes.sum():
            thresh_min = len(batches_volumes) - 1
            thresh_max = len(batches_volumes) - 1

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
    def prepare_data_and_optimize(data, unit):
        volumes, emissions, lot_ids, enforced_volumes, target_volume = TeneurService.prepare_data(data, unit)

        # Transform saved emissions (tCO2) into emissions per energy (gCO2/MJ)
        pci = data["biofuel"].pci_litre
        volume_energy = target_volume * pci  # MJ
        target_emission = GHG_REFERENCE_RED_II - (data["target_emission"] * 1000000 / volume_energy)  # gCO2/MJ emis

        selected_lots, fun = TeneurService.optimize_biofuel_blending(
            volumes,
            emissions,
            target_volume,
            target_emission,
            enforced_volumes,
            data.get("max_n_batches", None),
        )

        return selected_lots, lot_ids, emissions, fun

    @staticmethod
    def get_min_and_max_emissions(entity_id, data, unit):
        """
        Compute minimum and maximum feasible mix emissions.
        Return avoided emissions (tCO2)
        """
        volumes, emissions, _, _, target_volume = TeneurService.prepare_data(
            data,
            unit,
        )  # volumes in L, emissions in gCO2/MJ

        min_emissions_rate, max_emissions_rate = TeneurService.emission_bounds(
            volumes,
            emissions,
            target_volume,
        )

        max_avoided_emissions = TeneurService.convert_producted_emissions_to_avoided_emissions(
            target_volume, data["biofuel"], min_emissions_rate
        )
        min_avoided_emissions = TeneurService.convert_producted_emissions_to_avoided_emissions(
            target_volume, data["biofuel"], max_emissions_rate
        )

        return min_avoided_emissions, max_avoided_emissions

    @staticmethod
    def convert_producted_emissions_to_avoided_emissions(volume, biofuel, emissions_rate):
        """
        Convert producted emissions (gCO2/MJ) into avoided emissions (tCO2)
        """
        pci = biofuel.pci_litre
        volume_energy = volume * pci  # MJ
        return (GHG_REFERENCE_RED_II - emissions_rate) * volume_energy / 1000000  # tCO2

    @staticmethod
    def prepare_data(data, unit):
        """
        Prepare data for optimization and operation creation
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

        # Commented out because we don't want to filter by depot anymore (for now)
        # if data.get("from_depot") is not None:
        #     operations = operations.filter(to_depot=data["from_depot"])

        ges_bound_min = data.get("ges_bound_min", None)
        ges_bound_max = data.get("ges_bound_max", None)

        # Calculate balance of debited entity, for each lot, always in liters
        balance = BalanceService.calculate_balance(
            operations,
            data["debited_entity"].id,
            "lot",
            "l",
            None,
            ges_bound_min,
            ges_bound_max,
        )

        # Rearrange balance in an array of all volumes sums and an array of all ghg sums
        # For each we have something like:
        # array([30.52876597, 42.1162736 , 30.07384206, 25.05628985, 85.52717505])
        volumes, emissions, lot_ids = np.array([]), np.array([]), np.array([])
        enforced_volumes = np.array([]) if "enforced_volumes" in data else None

        for key, value in balance.items():
            sector, customs_cat, biofuel, lot_id = key

            volumes = np.append(volumes, value["available_balance"])
            emissions = np.append(emissions, value["emission_rate_per_mj"])
            lot_ids = np.append(lot_ids, lot_id)

            if enforced_volumes is not None:
                volume = value["available_balance"] if lot_id in data["enforced_volumes"] else 0
                enforced_volumes = np.append(enforced_volumes, volume)

        # Convert target volume into L
        target_volume = None
        if data.get("target_volume", None) is not None:
            target_volume = TeneurService._convert_in_liters(data["target_volume"], unit, data["biofuel"])

        return volumes, emissions, lot_ids, enforced_volumes, target_volume

    @staticmethod
    def _convert_in_liters(quantity, unit, biofuel):
        if unit == "mj":
            return quantity / biofuel.pci_litre
        elif unit == "kg":
            return quantity / biofuel.masse_volumique
        else:
            return quantity
