import { ElecOperationSector, OperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"

export interface BaseObjective {
  target: number
  teneur_declared: number // GJ
  quantity_available: number // GJ
  teneur_declared_month: number // GJ
  target_percent: number
  penalty: number // euro cents
}
export interface CategoryObjective extends BaseObjective {
  code: CategoryEnum
}

export interface SectorObjective extends BaseObjective {
  code: OperationSector
}

export interface MainObjective extends BaseObjective {
  energy_basis: number // GJ
}

export interface ElecCategoryObjective
  extends Omit<BaseObjective, "target" | "target_percent"> {
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

export enum TargetType {
  REACH = "REACH",
  CAP = "CAP",
}
