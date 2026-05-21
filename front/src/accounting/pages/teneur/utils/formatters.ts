import { CategoryObjective, SectorObjective } from "../types"
import { floorNumber } from "common/utils/formatters"

// Calculate the amount of energy before reaching the objective or the limit
export const computeObjectiveEnergy = (
  objective: CategoryObjective | SectorObjective
) =>
  floorNumber(objective.target, 0) -
  floorNumber(objective.teneur_declared, 0) -
  floorNumber(objective.pending_teneur, 0)
