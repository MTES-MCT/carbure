import { api } from "common/services/api-fetch"
import { BiomethaneEnergyAddRequest } from "./types"

export const getYears = (entity_id: number) =>
  api.GET("/biomethane/energy/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getEnergy = (entity_id: number, year: number) =>
  api
    .GET("/biomethane/energy/", {
      params: {
        query: {
          entity_id,
          year,
        },
      },
    })
    .then((res) => res.data)

export const saveEnergy = (
  entity_id: number,
  body: BiomethaneEnergyAddRequest
) =>
  api.PUT("/biomethane/energy/", {
    params: {
      query: {
        entity_id,
      },
    },
    body,
  })

export const validateEnergy = (entity_id: number) =>
  api.POST("/biomethane/energy/validate/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
