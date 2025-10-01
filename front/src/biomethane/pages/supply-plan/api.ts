import { api, download } from "common/services/api-fetch"
import {
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
} from "./types"

export const getSupplyPlanYears = async (entity_id: number) =>
  api.GET("/biomethane/supply-plan/years/", {
    params: { query: { entity_id } },
  })

export const getSupplyPlanInputs = async (query: BiomethaneSupplyInputQuery) =>
  api
    .GET("/biomethane/supply-input/", {
      params: { query },
    })
    .then((res) => res.data)

export const getSupplyPlanInputFilters = async (
  query: BiomethaneSupplyInputQuery,
  filter: BiomethaneSupplyInputFilter
) =>
  api
    .GET("/biomethane/supply-input/filters/", {
      params: {
        query: {
          ...query,
          filter,
        },
      },
    })
    .then((res) => res.data ?? [])

export function downloadSupplyPlan(query: BiomethaneSupplyInputQuery) {
  return download(`/biomethane/supply-input/export/`, {
    ...query,
  })
}

export const importSupplyPlan = async (entity_id: number, file: File) => {
  await api.POST("/biomethane/supply-plan/import/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: {
      file,
    },
  })
}
