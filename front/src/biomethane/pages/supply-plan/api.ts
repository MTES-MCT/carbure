import { api, download } from "common/services/api-fetch"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputFilter,
  BiomethaneSupplyInputQuery,
} from "./types"

export const getSupplyPlanInputs = async (
  query: BiomethaneSupplyInputQuery,
  selectedEntityId?: number
) =>
  api
    .GET("/biomethane/supply-input/", {
      params: {
        query: { ...query, producer_id: selectedEntityId },
      },
    })
    .then((res) => res.data)

export const getSupplyPlanInputFilters = async (
  query: BiomethaneSupplyInputQuery,
  filter: BiomethaneSupplyInputFilter,
  selected_entity_id?: number
) =>
  api
    .GET("/biomethane/supply-input/filters/", {
      params: {
        query: {
          ...query,
          filter,
          producer_id: selected_entity_id,
        },
      },
    })
    .then((res) => res.data ?? [])

export const getSupplyInput = async (
  entity_id: number,
  supply_input_id: number,
  selected_entity_id?: number
) =>
  api
    .GET("/biomethane/supply-input/{id}/", {
      params: {
        path: {
          id: supply_input_id,
        },
        query: { entity_id, producer_id: selected_entity_id },
      },
    })
    .then((res) => res.data)

export const createSupplyInput = async (
  entity_id: number,
  year: number,
  data: BiomethaneSupplyInput
) =>
  api
    .POST("/biomethane/supply-input/", {
      params: { query: { entity_id, year } },
      body: {
        ...data,
        origin_country: data.origin_country?.code_pays,
        input_name: data.input_name?.name ?? "",
      },
    })
    .then((res) => res.data)

export const saveSupplyInput = async (
  entity_id: number,
  year: number,
  supply_input_id: number,
  data: BiomethaneSupplyInput
) =>
  api
    .PATCH("/biomethane/supply-input/{id}/", {
      params: {
        path: { id: supply_input_id },
        query: { entity_id, year },
      },
      body: { ...data, origin_country: data.origin_country?.code_pays },
    })
    .then((res) => res.data)

export function downloadSupplyPlan(
  query: BiomethaneSupplyInputQuery,
  selectedEntityId?: number
) {
  return download(`/biomethane/supply-input/export/`, {
    ...query,
    producer_id: selectedEntityId,
  })
}

export const importSupplyPlan = async (
  entity_id: number,
  year: number,
  file: File
) => {
  await api.POST("/biomethane/supply-plan/import/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body: {
      file,
    },
  })
}
