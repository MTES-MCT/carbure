import { getBalances } from "accounting/api/balances"
import { CategoryEnum, Unit } from "common/types"
import {
  CategoryObjective,
  Objectives,
  UnconstrainedCategoryObjective,
} from "./types"
import { api } from "common/services/api-fetch"
import { BalancesGroupBy } from "accounting/types"
import { apiTypes } from "common/services/api-fetch.types"
import { CONVERSIONS } from "common/utils/formatters"

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
          target_percent: objectives?.main.target_percent
            ? objectives?.main.target_percent * 100
            : 0,
        },
        sectors:
          objectives?.sectors.map((sector) => ({
            code: sector.code,
            target: CONVERSIONS.energy.MJ_TO_GJ(sector.objective.target_mj),
            teneur_declared: CONVERSIONS.energy.MJ_TO_GJ(
              sector.declared_teneur
            ),
            teneur_declared_month: CONVERSIONS.energy.MJ_TO_GJ(
              sector.pending_teneur
            ),
            quantity_available: CONVERSIONS.energy.MJ_TO_GJ(
              sector.available_balance
            ),
            target_percent: sector.objective.target_percent * 100, // Percentage of the total target to consider
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
          if (
            category.objective.target_mj &&
            category.objective.target_mj === 0
          ) {
            return objCategories
          }

          const cat = {
            code: category.code,
            target: category.objective.target_mj
              ? CONVERSIONS.energy.MJ_TO_GJ(category.objective.target_mj)
              : 0,
            teneur_declared: CONVERSIONS.energy.MJ_TO_GJ(
              category.declared_teneur
            ),
            teneur_declared_month: CONVERSIONS.energy.MJ_TO_GJ(
              category.pending_teneur
            ),
            quantity_available: CONVERSIONS.energy.MJ_TO_GJ(
              category.available_balance
            ),
          }
          if (!category.objective.target_mj) {
            objCategories.unconstrained_categories.push({ ...cat, target: 0 })
          } else {
            const categoryMapping = {
              REACH: "objectivized_categories",
              CAP: "capped_categories",
              OTHER: "unconstrained_categories",
            } as const
            const categoryType =
              categoryMapping[
                category.objective.target_type as keyof typeof categoryMapping
              ]

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
    unit: Unit.MJ,
  })
}

export const getBalancesBySector = async (entity_id: number) => {
  return getBalances<apiTypes["BalanceBySector"]>({
    entity_id,
    page: 1,
    group_by: BalancesGroupBy.sector,
    unit: Unit.MJ,
  })
}

export const validateTeneurBiofuel = async (entity_id: number) => {
  return api.POST("/tiruert/operations/teneur/declare/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}
export const validateTeneurElec = async (entity_id: number) => {
  return api.POST("/tiruert/elec-operations/teneur/declare/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}
