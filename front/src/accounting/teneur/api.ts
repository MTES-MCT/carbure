import { OperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"

type Objectives = {
  global: {
    objective: number // tCO2
    teneur_declared: number // TC02
    quantity_available: number // tC02
    teneur_declared_month: number // TC02
  }
  sectors: {
    code: OperationSector
    objective: number // GJ
    teneur_declared: number // GJ
    quantity_available: number // GJ
    teneur_declared_month: number // GJ
  }[]
  capped_categories: {
    code: CategoryEnum
    limit: number // GJ
    teneur_declared: number // GJ
    quantity_available: number // GJ
    teneur_declared_month: number // GJ
  }[]
  objectivized_categories: {
    code: CategoryEnum
    objective: number // GJ
    teneur_declared: number // GJ
    quantity_available: number // GJ
    teneur_declared_month: number // GJ
  }[]
  unconstrained_categories: {
    code: CategoryEnum
    teneur_declared: number // GJ
    teneur_declared_month: number // GJ
    quantity_available: number // GJ
  }[]
}

export const getObjectives = async (
  entity_id: number,
  year: number
): Promise<Objectives> => {
  return new Promise((resolve) => {
    resolve({
      global: {
        objective: 16, // tCO2
        teneur_declared: 1, // TC02
        teneur_declared_month: 14, // TC02
        quantity_available: 100, // tC02
      },
      sectors: [
        {
          code: OperationSector.ESSENCE,
          objective: 9, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 4000, // GJ
          teneur_declared_month: 2, // GJ
        },
        {
          code: OperationSector.DIESEL,
          objective: 12, // GJ
          teneur_declared: 3, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
        {
          code: OperationSector.SAF,
          objective: 12, // GJ
          teneur_declared: 4, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 8, // GJ
        },
      ],
      capped_categories: [
        {
          code: CategoryEnum.TALLOL,
          limit: 12, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
        {
          code: CategoryEnum.ANN_IX_A,
          limit: 8, // GJ
          teneur_declared: 1, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 2, // GJ
        },
        {
          code: CategoryEnum.CONV,
          limit: 8, // GJ
          teneur_declared: 8, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
        {
          code: CategoryEnum.EP2AM,
          limit: 8, // GJ
          teneur_declared: 8, // GJ
          quantity_available: 2500, // GJ
          teneur_declared_month: 0, // GJ
        },
      ],
      objectivized_categories: [
        {
          code: CategoryEnum.ANN_IX_B,
          objective: 12, // GJ
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
        },
      ],
    })
  })
}

export const getBiofuelsCategory = async () => {}
