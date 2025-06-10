import { getBalances } from "accounting/api/balances"
import { getElecBalances } from "accounting/api/elec-balances"
import { CategoryEnum, Unit } from "common/types"
import {
  CategoryObjective,
  Objectives,
  UnconstrainedCategoryObjective,
} from "./types"
import { api } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"
import { CONVERSIONS } from "common/utils/formatters"

function parseObjectivesResponse(objectives: any) {
  const baseObjective = {
    global: {
      target: objectives?.main.target ?? 0,
      teneur_declared: objectives?.main.declared_teneur ?? 0,
      teneur_declared_month: objectives?.main.pending_teneur ?? 0,
      quantity_available: objectives?.main.available_balance ?? 0,
      target_percent: objectives?.main.target_percent
        ? objectives?.main.target_percent * 100
        : 0,
      penalty: objectives?.main.penalty ?? 0,
      energy_basis: CONVERSIONS.energy.MJ_TO_GJ(
        objectives?.main.energy_basis ?? 0
      ),
    },
    sectors:
      objectives?.sectors.map((sector: any) => ({
        code: sector.code,
        target: CONVERSIONS.energy.MJ_TO_GJ(sector.objective.target_mj),
        teneur_declared: CONVERSIONS.energy.MJ_TO_GJ(sector.declared_teneur),
        teneur_declared_month: CONVERSIONS.energy.MJ_TO_GJ(
          sector.pending_teneur
        ),
        quantity_available: CONVERSIONS.energy.MJ_TO_GJ(
          sector.available_balance
        ),
        target_percent: sector.objective.target_percent * 100,
        penalty: sector.objective.penalty ?? 0,
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
    objectives?.categories.reduce(
      (objCategories: typeof defaultCategories, category: any) => {
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
          target_percent: category.objective.target_percent * 100,
          penalty: category.objective.penalty ?? 0,
        }
        if (!category.objective.target_mj) {
          objCategories.unconstrained_categories.push({
            ...cat,
            target: null,
            target_percent: null,
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
      },
      defaultCategories
    ) ?? defaultCategories

  return {
    ...baseObjective,
    ...categories,
  }
}

type ObjectivesEndpoint =
  | "/tiruert/objectives/"
  | "/tiruert/admin-objectives/"
  | "/tiruert/admin-objectives-entity/"

type ObjectivesParams = {
  entity_id: number
  year: string
  date_from: string
  date_to: string
}

type AdminObjectivesParams = ObjectivesParams

type AdminObjectivesEntityParams = ObjectivesParams & {
  selected_entity_id: number
}

async function fetchObjectives(
  endpoint: ObjectivesEndpoint,
  params: ObjectivesParams | AdminObjectivesParams | AdminObjectivesEntityParams
): Promise<Objectives> {
  return api
    .GET(endpoint, { params: { query: params } })
    .then((res) => parseObjectivesResponse(res?.data))
}

export const getObjectives = async (
  entity_id: number,
  year: number,
  isAdmin?: boolean
): Promise<Objectives> => {
  const params = {
    entity_id,
    year: `${year}`,
    date_from: `${year}-01-01`,
    date_to: `${year}-12-31`,
  }

  if (isAdmin) {
    return fetchObjectives("/tiruert/admin-objectives/", params)
  } else {
    return fetchObjectives("/tiruert/objectives/", params)
  }
}

export const getAdminObjectivesEntity = async (
  entity_id: number,
  year: number,
  selected_entity_id: number
): Promise<Objectives> => {
  const params = {
    entity_id,
    year: `${year}`,
    date_from: `${year}-01-01`,
    date_to: `${year}-12-31`,
    selected_entity_id,
  }

  return fetchObjectives("/tiruert/admin-objectives-entity/", params)
}

/**
  Get the balances for a category (used to get the biofuels category)
 */
export const getBalancesCategory = async (
  entity_id: number,
  category: CategoryEnum,
  gesBoundMin?: number,
  gesBoundMax?: number
) => {
  return getBalances({
    entity_id,
    page: 1,
    customs_category: [category],
    unit: Unit.MJ,
    ges_bound_min: gesBoundMin,
    ges_bound_max: gesBoundMax,
  })
}

export const getBiofuelBalance = async (entity_id: number) => {
  return getBalances<apiTypes["Balance"]>({
    entity_id,
    unit: Unit.MJ,
  })
}

export const getElecBalance = (entity_id: number) => {
  return getElecBalances({ entity_id })
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

export const downloadMacFossilFuel = (entity_id: number) => {
  window.open(
    `/api/tiruert/mac-fossil-fuel/export/?entity_id=${entity_id}`,
    "_blank",
    "noopener,noreferrer"
  )
}
