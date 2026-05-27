import { CategoryEnum } from "common/types"
import { OperationSector } from "accounting/types"
import {
  CategoryObjective,
  MainObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../types"
import { withObjectiveProgress } from "../utils/formatters"

export const cappedCategories: CategoryObjective[] = [
  withObjectiveProgress({
    code: CategoryEnum.CONV,
    target: 4214.565651000001,
    teneur_declared: 4.988000000000159,
    pending_teneur: 50,
    quantity_available: 4723.8037557404,
    target_percent: 0.67,
    penalty: 0,
    target_type: TargetType.CAP,
  }),
]

export const cappedCategoryWithLimitReached: CategoryObjective =
  withObjectiveProgress({
    code: CategoryEnum.CONV,
    target: 100,
    teneur_declared: 80,
    pending_teneur: 25,
    quantity_available: 0,
    target_percent: 0.67,
    penalty: 0,
    target_type: TargetType.CAP,
  })

export const unconstrainedCategories: UnconstrainedCategoryObjective[] = [
  withObjectiveProgress({
    code: CategoryEnum.OTHER,
    target: null,
    teneur_declared: 10000,
    pending_teneur: 0,
    quantity_available: 357637.20670999994,
    target_percent: null,
    penalty: 0,
    target_type: null,
  }),
  withObjectiveProgress({
    code: CategoryEnum.ANN_IX_B,
    target: null,
    teneur_declared: 0,
    pending_teneur: 0,
    quantity_available: 135531.468,
    target_percent: null,
    penalty: 0,
    target_type: null,
  }),
]

export const objectivizedCategories: CategoryObjective[] = [
  withObjectiveProgress({
    code: CategoryEnum.ANN_IX_A,
    target: 19667.973038,
    teneur_declared: 144.00000000000003,
    pending_teneur: 0,
    quantity_available: 541168.905,
    target_percent: 0.67,
    penalty: 0,
    target_type: TargetType.REACH,
  }),
]

export const overallObjective: MainObjective = withObjectiveProgress({
  target: 38296.35321542,
  teneur_declared: 954.004872,
  pending_teneur: 45.7,
  quantity_available: 141631.71604577947,
  target_percent: 0.67,
  penalty: 0,
  energy_basis: 0,
})

export const defaultCategoryObjective: CategoryObjective =
  withObjectiveProgress({
    code: CategoryEnum.CONV,
    target: 300,
    teneur_declared: 20,
    pending_teneur: 10,
    quantity_available: 1000,
    target_percent: 10,
    penalty: 0,
    target_type: TargetType.CAP,
  })

export const defaultSectorObjectives: SectorObjective[] = [
  withObjectiveProgress({
    code: OperationSector.ESSENCE,
    target: 400,
    teneur_declared: 30,
    pending_teneur: 20,
    quantity_available: 1200,
    target_percent: 12,
    penalty: 0,
  }),
]

export const defaultMainObjective: MainObjective = withObjectiveProgress({
  target: 150,
  teneur_declared: 20,
  pending_teneur: 10,
  quantity_available: 500,
  target_percent: 5,
  penalty: 0,
  energy_basis: 1000,
})

export const defaultTargetType = TargetType.CAP
