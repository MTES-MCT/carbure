import { CategoryObjective, SectorObjective } from "../types"
import { floorNumber } from "common/utils/formatters"
// Calculate the amount of energy before reaching the objective or the limit
export const computeObjectiveEnergy = (
  objective: CategoryObjective | SectorObjective,
  formatter = floorNumber
) =>
  formatter(objective.target, 0) -
  formatter(objective.teneur_declared, 0) -
  formatter(objective.teneur_declared_month, 0)
