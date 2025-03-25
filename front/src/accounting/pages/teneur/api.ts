import { getBalances } from "accounting/api/balances"
import { PathsApiTiruertOperationsGetParametersQueryUnit } from "api-schema"
import { CategoryEnum } from "common/types"
import {
  CategoryObjective,
  Objectives,
  UnconstrainedCategoryObjective,
} from "./types"
import { api } from "common/services/api-fetch"
import { BalancesGroupBy } from "accounting/types"
import { apiTypes } from "common/services/api-fetch.types"

export const getObjectives = async (
  entity_id: number,
  year: number
): Promise<Objectives> => {
  return api
    .GET("/tiruert/objectives/", {
      params: {
        query: {
          entity_id,
          year: `${year}`,
          date_from: `${year}-01-01`,
          date_to: `${year}-12-31`,
        },
      },
    })
    .then((res) => {
      const objectives = res?.data

      const baseObjective = {
        global: {
          target: objectives?.main.target ?? 0,
          teneur_declared: objectives?.main.declared_teneur ?? 0,
          teneur_declared_month: objectives?.main.pending_teneur ?? 0,
          quantity_available: objectives?.main.available_balance ?? 0,
        },
        sectors:
          objectives?.sectors.map((sector) => ({
            code: sector.code,
            target: sector.objective.target_mj,
            teneur_declared: sector.declared_teneur,
            teneur_declared_month: sector.pending_teneur,
            quantity_available: sector.available_balance,
          })) ?? [],
      }

      const defaultCategories: {
        objectivized_categories: CategoryObjective[]
        capped_categories: CategoryObjective[]
        unconstrained_categories: UnconstrainedCategoryObjective[]
      } = {
        objectivized_categories: [],
        capped_categories: [],
        unconstrained_categories: [],
      }

      const categories =
        objectives?.categories.reduce((objCategories, category) => {
          const cat = {
            code: category.code,
            target: category.objective.target_mj ?? null,
            teneur_declared: category.declared_teneur,
            teneur_declared_month: category.pending_teneur,
            quantity_available: category.available_balance,
          }
          if (!category.objective.target_mj) {
            objCategories.unconstrained_categories.push({
              ...cat,
              target: null,
            })
          } else {
            const categoryMapping = {
              REACH: "objectivized_categories",
              CAP: "capped_categories",
            }
            const categoryType = categoryMapping[
              category.objective.target_type as keyof typeof categoryMapping
            ] as "capped_categories" | "objectivized_categories"

            objCategories[categoryType].push(cat)
          }
          return objCategories
        }, defaultCategories) ?? defaultCategories

      return {
        ...baseObjective,
        ...categories,
      }
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

export const getBalancesBySector = async (entity_id: number) => {
  return getBalances<apiTypes["BalanceBySector"]>({
    entity_id,
    page: 1,
    group_by: BalancesGroupBy.sector,
    // TODO: change in the backend to use the same enum as the entity
    unit: PathsApiTiruertOperationsGetParametersQueryUnit.mj,
  })
}
