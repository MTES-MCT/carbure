import { api } from "common/services/api-fetch"

export const getYears = (entity_id: number) =>
  api.GET("/biomethane/digestate/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
