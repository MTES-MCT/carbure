import { api } from "common/services/api-fetch"

export const getAnnualDeclarationYears = (entity_id: number) =>
  api.GET("/biomethane/annual-declaration/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
