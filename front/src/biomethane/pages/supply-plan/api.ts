import { api } from "common/services/api-fetch"

export const getSupplyPlanYears = async (entity_id: number) =>
  api.GET("/biomethane/supply-plan/years/", {
    params: { query: { entity_id } },
  })

export const getSupplyPlanInputs = async (entity_id: number, year: number) =>
  api
    .GET("/biomethane/supply-input/", {
      params: { query: { entity_id, year: year.toString() } },
    })
    .then((res) => res.data)
