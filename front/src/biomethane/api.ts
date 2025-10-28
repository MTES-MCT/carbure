import { BiomethaneAnnualDeclarationStatusEnum } from "api-schema"
import { api } from "common/services/api-fetch"

export const getAnnualDeclarationYears = (entity_id: number) =>
  api.GET("/biomethane/annual-declaration/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getCurrentAnnualDeclaration = (entity_id: number) =>
  api
    .GET("/biomethane/annual-declaration/", {
      params: {
        query: {
          entity_id,
        },
      },
    })
    .then((response) => response.data)

export const validateAnnualDeclaration = (entity_id: number) =>
  api.POST("/biomethane/annual-declaration/validate/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const correctAnnualDeclaration = (entity_id: number) =>
  api.PATCH("/biomethane/annual-declaration/", {
    params: {
      query: {
        entity_id,
      },
    },
    body: {
      status: BiomethaneAnnualDeclarationStatusEnum.IN_PROGRESS,
    },
  })
