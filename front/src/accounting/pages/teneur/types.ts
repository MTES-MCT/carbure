import { OperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"

export interface BaseObjective {
  target: number
  teneur_declared: number // GJ
  quantity_available: number // GJ
  teneur_declared_month: number // GJ
}
export interface CategoryObjective extends BaseObjective {
  code: CategoryEnum
}

export interface SectorObjective extends BaseObjective {
  code: OperationSector
  target_percent: number
}

export interface MainObjective extends BaseObjective {
  target_percent: number
}

export type UnconstrainedCategoryObjective = CategoryObjective

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
