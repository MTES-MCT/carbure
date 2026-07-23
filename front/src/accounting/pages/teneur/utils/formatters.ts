import { FRACTION_DIGITS_GJ, FRACTION_DIGITS_LITERS } from "accounting/config"
import { BaseObjective, ObjectiveProgress } from "../types"
import { ExtendedUnit } from "common/types"
import { ceilNumber, CONVERSIONS, formatUnit } from "common/utils/formatters"
import { formatAccountingUnit } from "accounting/utils/formatters"

type ObjectiveProgressInput = Pick<
  BaseObjective,
  "teneur_declared" | "pending_teneur" | "quantity_available"
> & {
  target?: number | null
}

export const computeObjectiveProgress = (
  objective: ObjectiveProgressInput
): ObjectiveProgress => {
  const base_quantity = objective.teneur_declared
  const declared_quantity = objective.pending_teneur
  const target_quantity = objective.target ?? 0
  const total_teneur_declared =
    objective.teneur_declared + objective.pending_teneur
  const remaining_energy = Math.max(
    0,
    target_quantity - base_quantity - declared_quantity
  )

  const quantity_available = objective.quantity_available

  // If the target is not set, the objective is not met
  const is_objective_met =
    objective.target && objective.target > 0
      ? objective.pending_teneur + objective.teneur_declared >=
        (objective.target ?? 0)
      : false

  return {
    total_teneur_declared,
    base_quantity,
    target_quantity,
    declared_quantity,
    remaining_energy,
    is_objective_met,
    quantity_available,
  }
}

export const formatObjectiveGJ = (value: number) =>
  formatAccountingUnit(value, ExtendedUnit.GJ)

export const formatObjectiveCO2 = (value: number) =>
  formatUnit(value, ExtendedUnit.tCO2ev, { fractionDigits: 0 })

export const computeEnergyGjFromLiters = (
  quantityLiters: number,
  pciLitre: number
) =>
  ceilNumber(
    CONVERSIONS.energy.MJ_TO_GJ(quantityLiters * pciLitre),
    FRACTION_DIGITS_GJ
  )

/** Remaining energy (MJ) / PCI → liters, rounded up to 2 decimal places. */
export const computeRemainingLitersFromMj = (
  remainingMj: number,
  pciLitre: number
) => ceilNumber(remainingMj / pciLitre, FRACTION_DIGITS_LITERS)

/** Remaining cap (GJ) → max liters, rounded up to 2 decimal places. */
export const computeLitersMaxFromEnergyGj = (
  energyGj: number,
  pciLitre: number
) => computeRemainingLitersFromMj(energyGj * 1000, pciLitre)

export const computeObjectiveEnergy = (objective: ObjectiveProgressInput) =>
  computeObjectiveProgress(objective).remaining_energy

/**
 * Compute the remaining energy after the additional quantity is declared
 * @param objective - The objective progress
 * @param additionalQuantity - The additional quantity declared
 * @returns The remaining energy
 */
export const computeRemainingEnergyWithAdditionalQuantity = (
  objective: {
    target: number
    teneur_declared: number
    pending_teneur: number
  },
  additionalQuantity: number
) => {
  console.log("objectives", objective)

  return Math.max(
    0,
    computeObjectiveEnergy({ ...objective, quantity_available: 0 }) -
      additionalQuantity
  )
}

export const withObjectiveProgress = <T extends ObjectiveProgressInput>(
  objective: T
): T & { progress: ObjectiveProgress } => ({
  ...objective,
  progress: computeObjectiveProgress(objective),
})
