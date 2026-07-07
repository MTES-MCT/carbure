import { ElecOperationSector, OperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"
import { apiTypes } from "common/services/api-fetch.types"

export { TargetTypeEnum as TargetType } from "api-schema"

export type FossilFuel = apiTypes["FossilFuel"]

export interface ObjectiveProgress {
  total_teneur_declared: number
  base_quantity: number
  target_quantity: number
  declared_quantity: number
  remaining_energy: number
  is_objective_met: boolean
  quantity_available: number
}

export interface BaseObjective {
  target: number
  teneur_declared: number // GJ
  quantity_available: number // GJ
  pending_teneur: number // GJ
  target_percent: number
  penalty: number // euro cents
  progress: ObjectiveProgress
}
export interface CategoryObjective extends BaseObjective {
  code: CategoryEnum
  target_type: apiTypes["Objective"]["target_type"]
}

export interface SectorObjective extends BaseObjective {
  code: OperationSector
}

export interface MainObjective extends BaseObjective {
  energy_basis: number // GJ
}

export interface ElecCategoryObjective extends Omit<
  BaseObjective,
  "target" | "target_percent"
> {
  code: ElecOperationSector.ELEC
  target: null
  target_percent: null
}

export type BiofuelUnconstrainedCategoryObjective = Omit<
  CategoryObjective,
  "target" | "target_percent"
> & {
  target: null
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
