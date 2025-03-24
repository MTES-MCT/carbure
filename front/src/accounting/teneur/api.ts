import { getBalances } from "accounting/api/balances"
import { OperationSector } from "accounting/types"
import { PathsApiTiruertOperationsGetParametersQueryUnit } from "api-schema"
import { CategoryEnum } from "common/types"
import { CategoryObjective, Objectives } from "./types"
import { api } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"

export const getObjectives = async (
  entity_id: number,
  year: number
): Promise<Objectives> => {
  // return api
  //   .GET("/tiruert/objectives/", {
  //     params: {
  //       query: {
  //         entity_id,
  //         year: `${year}`,
  //         date_from: `${year}-01-01`,
  //         date_to: `${year}-12-31`,
  //       },
  //     },
  //   })
  //   .then((res) => {
  //     const objectives = res?.data && res.data.length > 0 ? res.data[0] : null
  //     if (!objectives) {
  //       throw new Error("No objectives found")
  //     }

  //     const baseObjective = {
  //       global: {
  //         target: objectives.main.target,
  //         teneur_declared: objectives.main.declared_teneur,
  //         teneur_declared_month: objectives.main.pending_teneur,
  //         quantity_available: objectives.main.available_balance,
  //       },
  //       sectors: objectives.sectors.map((sector) => ({
  //         code: sector.code,
  //         target: sector.objective,
  //         teneur_declared: sector.declared_teneur,
  //         teneur_declared_month: sector.pending_teneur,
  //         quantity_available: sector.available_balance,
  //       })),
  //     }

  //     const defaultCategories: Record<
  //       | "objectivized_categories"
  //       | "capped_categories"
  //       | "unconstrained_categories",
  //       CategoryObjective[]
  //     > = {
  //       objectivized_categories: [],
  //       capped_categories: [],
  //       unconstrained_categories: [],
  //     }

  //     const categories = objectives.categories.reduce(
  //       (objCategories, category) => {
  //         const categoryMapping = {
  //           REACH: "objectivized_categories",
  //           CAP: "capped_categories",
  //         }
  //         const categoryType = (categoryMapping[
  //           category.objective.target_type as keyof typeof categoryMapping
  //         ] ?? "unconstrained_categories") as keyof typeof defaultCategories

  //         objCategories[categoryType].push({
  //           code: category.code as CategoryEnum,
  //           target: category.objective.target_mj ?? null,
  //           teneur_declared: category.declared_teneur,
  //           teneur_declared_month: category.pending_teneur,
  //           quantity_available: category.available_balance,
  //         })
  //         return objCategories
  //       },
  //       defaultCategories
  //     )

  //     return {
  //       ...baseObjective,
  //       ...categories,
  //     }
  //   })
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
          target: 9000,
          teneur_declared: 1000,
          quantity_available: 4000000,
          teneur_declared_month: 2000,
        },
        {
          code: OperationSector.DIESEL,
          target: 12000,
          teneur_declared: 3000,
          quantity_available: 2500000,
          teneur_declared_month: 0,
        },
        {
          code: OperationSector.SAF,
          target: 12000,
          teneur_declared: 4000,
          quantity_available: 2500000,
          teneur_declared_month: 8000,
        },
      ],
      capped_categories: [
        {
          code: CategoryEnum.TALLOL,
          target: 100000,
          teneur_declared: 5000,
          quantity_available: 2500000,
          teneur_declared_month: 0,
        },
        {
          code: CategoryEnum.ANN_IX_A,
          target: 666000,
          teneur_declared: 8000,
          quantity_available: 2500000,
          teneur_declared_month: 14000,
        },
        {
          code: CategoryEnum.CONV,
          target: 24000,
          teneur_declared: 8000,
          quantity_available: 2500000,
          teneur_declared_month: 0,
        },
        {
          code: CategoryEnum.EP2AM,
          target: 180000,
          teneur_declared: 18000,
          quantity_available: 2500000,
          teneur_declared_month: 0,
        },
      ],
      objectivized_categories: [
        {
          code: CategoryEnum.ANN_IX_B,
          target: 12458000,
          teneur_declared: 250000,
          quantity_available: 2500000,
          teneur_declared_month: 0,
        },
      ],
      unconstrained_categories: [
        {
          code: CategoryEnum.OTHER,
          teneur_declared: 1000,
          quantity_available: 80000,
          teneur_declared_month: 4000,
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
