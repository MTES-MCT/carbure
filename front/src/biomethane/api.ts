import { BiomethaneAnnualDeclarationStatusEnum } from "api-schema"
import { api } from "common/services/api-fetch"

export const getCurrentAnnualDeclaration = (
  entity_id: number,
  year: number | undefined
) =>
  api
    .GET("/biomethane/annual-declaration/", {
      params: {
        query: {
          entity_id,
          year,
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

export const correctAnnualDeclaration = (entity_id: number, year: number) =>
  api.PATCH("/biomethane/annual-declaration/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
    body: {
      status: BiomethaneAnnualDeclarationStatusEnum.IN_PROGRESS,
    },
  })
