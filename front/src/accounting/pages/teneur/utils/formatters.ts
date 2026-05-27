import { BaseObjective, ObjectiveProgress } from "../types"
import { ExtendedUnit } from "common/types"
import { floorNumber, formatUnit } from "common/utils/formatters"

type ObjectiveProgressInput = Pick<
  BaseObjective,
  "teneur_declared" | "pending_teneur"
> & {
  target?: number | null
}

export const computeObjectiveProgress = (
  objective: ObjectiveProgressInput
): ObjectiveProgress => {
  const base_quantity = floorNumber(objective.teneur_declared, 0)
  const declared_quantity = floorNumber(objective.pending_teneur, 0)
  const target_quantity = floorNumber(objective.target ?? 0, 0)
  const total_teneur_declared = floorNumber(
    objective.teneur_declared + objective.pending_teneur,
    0
  )
  const remaining_energy = Math.max(
    0,
    target_quantity - base_quantity - declared_quantity
  )

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
  }
}

export const formatObjectiveGJ = (value: number) =>
  formatUnit(value, ExtendedUnit.GJ, { fractionDigits: 0 })

export const computeObjectiveEnergy = (objective: ObjectiveProgressInput) =>
  computeObjectiveProgress(objective).remaining_energy

export const withObjectiveProgress = <T extends ObjectiveProgressInput>(
  objective: T
): T & { progress: ObjectiveProgress } => ({
  ...objective,
  progress: computeObjectiveProgress(objective),
})
