import { CategoryEnum } from "common/types"
import {
  CategoryObjective,
  MainObjective,
  UnconstrainedCategoryObjective,
} from "../types"

export const cappedCategories: CategoryObjective[] = [
  {
    code: CategoryEnum.CONV,
    target: 4214.565651000001,
    teneur_declared: 4.988000000000159,
    teneur_declared_month: 50,
    quantity_available: 4723.8037557404,
    target_percent: 0.67,
    penalty: 0,
  },
]

export const unconstrainedCategories: UnconstrainedCategoryObjective[] = [
  {
    code: CategoryEnum.OTHER,
    target: null,
    teneur_declared: 10000,
    teneur_declared_month: 0,
    quantity_available: 357637.20670999994,
    target_percent: null,
    penalty: 0,
  },
  {
    code: CategoryEnum.ANN_IX_B,
    target: null,
    teneur_declared: 0,
    teneur_declared_month: 0,
    quantity_available: 135531.468,
    target_percent: null,
    penalty: 0,
  },
]

export const objectivizedCategories: CategoryObjective[] = [
  {
    code: CategoryEnum.ANN_IX_A,
    target: 19667.973038,
    teneur_declared: 144.00000000000003,
    teneur_declared_month: 0,
    quantity_available: 541168.905,
    target_percent: 0.67,
    penalty: 0,
  },
]

export const overallObjective: MainObjective = {
  target: 38296.35321542,
  teneur_declared: 954.004872,
  teneur_declared_month: 45.7,
  quantity_available: 141631.71604577947,
  target_percent: 0.67,
  penalty: 0,
}
