import { getBalances } from "accounting/api/balances"
import { OperationSector } from "accounting/types"
import { PathsApiTiruertOperationsGetParametersQueryUnit } from "api-schema"
import { CategoryEnum } from "common/types"
import { Objectives } from "./types"

export const getObjectives = async (
  entity_id: number,
  year: number
): Promise<Objectives> => {
  return new Promise((resolve) => {
    resolve({
      global: {
        target: 16, // tCO2
        teneur_declared: 1, // TC02
        teneur_declared_month: 14, // TC02
        quantity_available: 100, // tC02
      },
      sectors: [
        {
          code: OperationSector.ESSENCE,
          target: 9, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 4000, // GJ
          teneur_declared_month: 2, // GJ
        },
        {
          code: OperationSector.DIESEL,
          target: 12, // GJ
          teneur_declared: 3, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
        {
          code: OperationSector.SAF,
          target: 12, // GJ
          teneur_declared: 4, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 8, // GJ
        },
      ],
      capped_categories: [
        {
          code: CategoryEnum.TALLOL,
          target: 12, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
        {
          code: CategoryEnum.ANN_IX_A,
          target: 8, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 2, // GJ
        },
        {
          code: CategoryEnum.CONV,
          target: 8, // GJ
          teneur_declared: 8, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
        {
          code: CategoryEnum.EP2AM,
          target: 8, // GJ
          teneur_declared: 8, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
      ],
      objectivized_categories: [
        {
          code: CategoryEnum.ANN_IX_B,
          target: 12, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
      ],
      unconstrained_categories: [
        {
          code: CategoryEnum.OTHER,
          teneur_declared: 1, // GJ
          quantity_available: 80, // GJ
          teneur_declared_month: 4, // GJ
          target: null,
        },
      ],
    })
  })
}

/**
  Get the balances for a category (used to get the biofuels category)
 */
export const getBalancesCategory = async (
  entity_id: number,
  category: CategoryEnum
) => {
  return getBalances({
    entity_id,
    page: 1,
    customs_category: [category],
    // TODO: change in the backend to use the same enum as the entity
    unit: PathsApiTiruertOperationsGetParametersQueryUnit.mj,
  })
}
