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
