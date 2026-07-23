import { CategoryEnum } from "common/types"
import { OperationSector } from "accounting/types"
import {
  CategoryObjective,
  MainObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../types"
import { enrichEnergyObjective, enrichMainObjective } from "../utils/formatters"

export const cappedCategories: CategoryObjective[] = [
  enrichEnergyObjective({
    code: CategoryEnum.CONV,
    target_mj: 4_214_566,
    teneur_declared_mj: 4_988,
    pending_teneur_mj: 50_000,
    quantity_available_mj: 4_723_804,
    target_percent: 0.67,
    penalty: 0,
    target_type: TargetType.CAP,
  }),
]

export const cappedCategoryWithLimitReached: CategoryObjective =
  enrichEnergyObjective({
    code: CategoryEnum.CONV,
    target_mj: 100_000,
    teneur_declared_mj: 80_000,
    pending_teneur_mj: 25_000,
    quantity_available_mj: 0,
    target_percent: 0.67,
    penalty: 0,
    target_type: TargetType.CAP,
  })

export const unconstrainedCategories: UnconstrainedCategoryObjective[] = [
  enrichEnergyObjective({
    code: CategoryEnum.OTHER,
    target_mj: null,
    teneur_declared_mj: 10_000_000,
    pending_teneur_mj: 0,
    quantity_available_mj: 357_637_207,
    target_percent: null,
    penalty: 0,
    target_type: null,
  }),
  enrichEnergyObjective({
    code: CategoryEnum.ANN_IX_B,
    target_mj: null,
    teneur_declared_mj: 0,
    pending_teneur_mj: 0,
    quantity_available_mj: 135_531_468,
    target_percent: null,
    penalty: 0,
    target_type: null,
  }),
]

export const objectivizedCategories: CategoryObjective[] = [
  enrichEnergyObjective({
    code: CategoryEnum.ANN_IX_A,
    target_mj: 19_667_973,
    teneur_declared_mj: 144_000,
    pending_teneur_mj: 0,
    quantity_available_mj: 541_168_905,
    target_percent: 0.67,
    penalty: 0,
    target_type: TargetType.REACH,
  }),
]

export const overallObjective: MainObjective = enrichMainObjective({
  target: 38296.35321542,
  teneur_declared: 954.004872,
  pending_teneur: 45.7,
  quantity_available: 141631.71604577947,
  target_percent: 0.67,
  penalty: 0,
  energy_basis_mj: 0,
})

export const defaultCategoryObjective: CategoryObjective =
  enrichEnergyObjective({
    code: CategoryEnum.CONV,
    target_mj: 300_000,
    teneur_declared_mj: 20_000,
    pending_teneur_mj: 10_000,
    quantity_available_mj: 1_000_000,
    target_percent: 10,
    penalty: 0,
    target_type: TargetType.CAP,
  })

export const defaultSectorObjectives: SectorObjective[] = [
  enrichEnergyObjective({
    code: OperationSector.ESSENCE,
    target_mj: 400_000,
    teneur_declared_mj: 30_000,
    pending_teneur_mj: 20_000,
    quantity_available_mj: 1_200_000,
    target_percent: 12,
    penalty: 0,
  }),
]

export const defaultMainObjective: MainObjective = enrichMainObjective({
  target: 150,
  teneur_declared: 20,
  pending_teneur: 10,
  quantity_available: 500,
  target_percent: 5,
  penalty: 0,
  energy_basis_mj: 1_000_000,
})

export const defaultTargetType = TargetType.CAP
