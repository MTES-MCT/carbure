import { FRACTION_DIGITS_LITERS } from "accounting/config"
import {
  EnergyObjectiveComputed,
  EnergyObjectiveFields,
  MainObjective,
} from "../types"
import { ExtendedUnit } from "common/types"
import { ceilNumber, formatUnit } from "common/utils/formatters"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { buildObjectiveProgressGj, mjToDisplayGj, remainingMj } from "./energy"

export type EnergyObjectiveInput = Pick<
  EnergyObjectiveFields,
  "teneur_declared_mj" | "pending_teneur_mj" | "quantity_available_mj"
> & {
  target_mj: number | null
}

type MainObjectiveInput = Pick<
  MainObjective,
  | "teneur_declared"
  | "pending_teneur"
  | "quantity_available"
  | "target"
  | "energy_basis_mj"
  | "target_percent"
  | "penalty"
>

export const enrichEnergyObjective = <T extends EnergyObjectiveInput>(
  objective: T
): T & EnergyObjectiveComputed => {
  const total_teneur_declared_mj =
    objective.teneur_declared_mj + objective.pending_teneur_mj
  const remaining_energy_mj = remainingMj(
    objective.target_mj ?? 0,
    objective.teneur_declared_mj,
    objective.pending_teneur_mj
  )
  const is_objective_met = Boolean(
    objective.target_mj &&
    objective.target_mj > 0 &&
    total_teneur_declared_mj >= objective.target_mj
  )

  const computed = {
    total_teneur_declared_mj,
    remaining_energy_mj,
    is_objective_met,
  }

  return {
    ...objective,
    ...computed,
    progress: buildObjectiveProgressGj({ ...objective, ...computed }),
  }
}

export const enrichMainObjective = <T extends MainObjectiveInput>(
  objective: T
): T &
  Pick<
    MainObjective,
    | "total_teneur_declared"
    | "remaining_energy"
    | "is_objective_met"
    | "energy_basis_gj"
  > => {
  const total_teneur_declared =
    objective.teneur_declared + objective.pending_teneur
  const remaining_energy = remainingMj(
    objective.target,
    objective.teneur_declared,
    objective.pending_teneur
  )
  const is_objective_met =
    objective.target > 0 ? total_teneur_declared >= objective.target : false

  return {
    ...objective,
    total_teneur_declared,
    remaining_energy,
    is_objective_met,
    energy_basis_gj: mjToDisplayGj(objective.energy_basis_mj),
  }
}

/** Format a pre-computed GJ value for display. */
export const formatObjectiveGJ = (gj: number) =>
  formatAccountingUnit(gj, ExtendedUnit.GJ)

/** Format a MJ value as GJ (for raw API balances not yet enriched). */
export const formatObjectiveGJFromMj = (mj: number) =>
  formatObjectiveGJ(mjToDisplayGj(mj))

export const formatObjectiveCO2 = (value: number) =>
  formatUnit(value, ExtendedUnit.tCO2ev, { fractionDigits: 0 })

export const computeEnergyGjFromLiters = (
  quantityLiters: number,
  pciLitre: number
) => mjToDisplayGj(quantityLiters * pciLitre)

export const computeEnergyMjFromLiters = (
  quantityLiters: number,
  pciLitre: number
) => quantityLiters * pciLitre

export const computeRemainingLitersFromMj = (
  remainingEnergyMj: number,
  pciLitre: number
) => ceilNumber(remainingEnergyMj / pciLitre, FRACTION_DIGITS_LITERS)

export const computeLitersMaxFromEnergyMj = (
  remainingEnergyMj: number,
  pciLitre: number
) => computeRemainingLitersFromMj(remainingEnergyMj, pciLitre)

export const remainingEnergyMjFrom = (objective: EnergyObjectiveInput) =>
  remainingMj(
    objective.target_mj ?? 0,
    objective.teneur_declared_mj,
    objective.pending_teneur_mj
  )

export const computeRemainingEnergyWithAdditionalQuantityMj = (
  objective: Pick<
    EnergyObjectiveFields,
    | "target_mj"
    | "teneur_declared_mj"
    | "pending_teneur_mj"
    | "quantity_available_mj"
  >,
  additionalMj: number
) => Math.max(0, remainingEnergyMjFrom(objective) - additionalMj)

export const remainingGjAfterAdditionalMj = (
  objective: Pick<
    EnergyObjectiveFields,
    "target_mj" | "teneur_declared_mj" | "pending_teneur_mj"
  >,
  additionalMj: number
) =>
  mjToDisplayGj(
    computeRemainingEnergyWithAdditionalQuantityMj(
      { ...objective, quantity_available_mj: 0 },
      additionalMj
    )
  )
