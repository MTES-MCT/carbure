import { ExtendedUnit, Unit } from "common/types"
import {
  CONVERSIONS,
  FormatNumberOptions,
  formatUnit,
} from "common/utils/formatters"
import { CategoryObjective } from "../types"

// Calculate the amount of energy before reaching the objective or the limit
export const computeObjectiveEnergy = (objective: CategoryObjective) =>
  objective.target - objective.teneur_declared - objective.teneur_declared_month

// Format the energy to the expected unit
// The energy property is always in MJ
export const formatEnergy = (
  energy: number,
  {
    unit = Unit.MJ,
    ...options
  }: {
    unit: Unit | ExtendedUnit
  } & FormatNumberOptions
) => {
  const convertedEnergy =
    unit === ExtendedUnit.GJ ? CONVERSIONS.energy.MJ_TO_GJ(energy) : energy

  return formatUnit(convertedEnergy, unit, options)
}
