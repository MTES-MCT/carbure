import { getBalances } from "accounting/api/biofuels/balances"
import { getElecBalances } from "accounting/api/elec/balances"
import { PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by } from "api-schema"
import { CategoryEnum } from "common/types"
import { Objectives } from "./types"
import { api } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"
import { parseObjectivesResponse } from "./utils/parse-objectives-response"

export const getObjectives = async (
  entity_id: number,
  year: number,
  selected_entity_id?: number
): Promise<Objectives> => {
  const params = {
    entity_id,
    year: `${year}`,
    ...(selected_entity_id !== undefined && { selected_entity_id }),
  }

  return api
    .GET("/tiruert/objectives/", { params: { query: params } })
    .then((res) => parseObjectivesResponse(res?.data))
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
    ges_bound_min: gesBoundMin,
    ges_bound_max: gesBoundMax,
  })
}

export const getBiofuelBalance = async (entity_id: number) => {
  return getBalances<apiTypes["Balance"]>({
    entity_id,
  })
}

export const getBiofuelBalancePerSector = async (entity_id: number) => {
  return getBalances<apiTypes["BalanceBySector"]>({
    entity_id,
    group_by: PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by.sector,
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
