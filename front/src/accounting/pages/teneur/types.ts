import { ElecOperationSector, OperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"
import { apiTypes } from "common/services/api-fetch.types"

export { TargetTypeEnum as TargetType } from "api-schema"

export type FossilFuel = apiTypes["FossilFuel"]

/** GJ values for display only — never use for arithmetic. */
export interface ObjectiveProgressGj {
  target: number
  teneur_declared: number
  pending_teneur: number
  quantity_available: number
  total_teneur_declared: number
  remaining_energy: number
}

export interface EnergyObjectiveFields {
  target_mj: number | null
  teneur_declared_mj: number
  pending_teneur_mj: number
  quantity_available_mj: number
  target_percent: number | null
  penalty: number // euro cents
}

export interface EnergyObjectiveComputed {
  total_teneur_declared_mj: number
  remaining_energy_mj: number
  is_objective_met: boolean
  progress: ObjectiveProgressGj
}

export interface EnergyObjective
  extends EnergyObjectiveFields, EnergyObjectiveComputed {}

export interface MainObjective {
  target: number // tCO2
  teneur_declared: number // tCO2
  quantity_available: number // tCO2
  pending_teneur: number // tCO2
  target_percent: number
  penalty: number // euro cents
  energy_basis_mj: number
  energy_basis_gj: number
  total_teneur_declared: number
  remaining_energy: number
  is_objective_met: boolean
}

export interface CategoryObjective extends EnergyObjective {
  code: CategoryEnum
  target_type: apiTypes["Objective"]["target_type"]
}

export interface SectorObjective extends EnergyObjective {
  code: OperationSector
}

export interface ElecCategoryObjective extends Omit<
  EnergyObjective,
  "target_mj" | "target_percent"
> {
  code: ElecOperationSector.ELEC
  target_mj: null
  target_percent: null
}

export type BiofuelUnconstrainedCategoryObjective = Omit<
  CategoryObjective,
  "target_mj" | "target_percent"
> & {
  target_mj: null
  target_percent: null
}

export type UnconstrainedCategoryObjective =
  | BiofuelUnconstrainedCategoryObjective
  | ElecCategoryObjective

export interface Objectives {
  global: MainObjective
  sectors: SectorObjective[]
  capped_categories: CategoryObjective[]
  objectivized_categories: CategoryObjective[]
  unconstrained_categories: UnconstrainedCategoryObjective[]
}
