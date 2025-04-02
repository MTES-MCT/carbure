import { CategoryObjective } from "../types"

// Calculate the amount of energy before reaching the objective or the limit
export const computeObjectiveEnergy = (objective: CategoryObjective) =>
  objective.target - objective.teneur_declared - objective.teneur_declared_month
