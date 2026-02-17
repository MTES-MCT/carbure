import { api } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"

export const getAnnualDeclarationYears = (entity_id: number) =>
  api.GET("/biomethane/annual-declaration/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getAnnualDeclaration = (
  entity_id: number,
  year: number | undefined,
  selected_entity_id?: number
) =>
  api
    .GET("/biomethane/annual-declaration/", {
      params: {
        query: {
          entity_id,
          year,
          producer_id: selected_entity_id,
        },
      },
    })
    .then((response) => response.data)

export const validateAnnualDeclaration = (entity_id: number, year: number) =>
  api.POST("/biomethane/annual-declaration/validate/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
  })

export const patchAnnualDeclaration = (
  entity_id: number,
  year: number,
  data: apiTypes["PatchedBiomethaneAnnualDeclarationRequest"],
  selected_entity_id?: number
) =>
  api.PATCH("/biomethane/annual-declaration/", {
    params: {
      query: {
        entity_id,
        year,
        producer_id: selected_entity_id,
      },
    },
    body: data,
  })
