import { getBalances } from "accounting/api/biofuels/balances"
import { getElecBalances } from "accounting/api/elec/balances"
import { CategoryEnum } from "common/types"
import { Objectives } from "./types"
import { api, getDownloadUrl } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"
import { OperationUnit } from "accounting/types"
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
    unit: OperationUnit.gj,
    ges_bound_min: gesBoundMin,
    ges_bound_max: gesBoundMax,
  })
}

export const getBiofuelBalance = async (entity_id: number) => {
  return getBalances<apiTypes["Balance"]>({
    entity_id,
    unit: OperationUnit.gj,
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

export const downloadMacFossilFuel = (entity_id: number, year: number) =>
  getDownloadUrl("/tiruert/mac-fossil-fuel/export/", { entity_id, year })

export type MacFossilFuel = {
  fuel: string
  volume: number
  year: number
  month: number
}

export const getMacFossilFuels = async (
  entity_id: number,
  year: number
): Promise<MacFossilFuel[]> => {
  return api
    .GET("/tiruert/mac-fossil-fuel/", {
      params: {
        query: {
          entity_id: `${entity_id}`,
          year,
          page_size: 1000,
        },
      },
    })
    .then(
      (res) =>
        res.data?.results.map((mac) => ({
          fuel: mac.fuel,
          volume: mac.volume ?? 0,
          year: mac.year,
          month: mac.period % 100,
        })) ?? []
    )
}

export const replaceMacFossilFuels = async (
  entity_id: number,
  year: number,
  macs: apiTypes["MacFossilFuelInputRequest"][]
) => {
  return api.PUT("/tiruert/mac-fossil-fuel/replace/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body: macs,
    bodySerializer: JSON.stringify,
  })
}
