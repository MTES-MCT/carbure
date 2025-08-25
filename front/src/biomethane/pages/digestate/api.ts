import { api } from "common/services/api-fetch"

export const getYears = (entity_id: number) =>
  api.GET("/biomethane/digestate/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })

export const getDigestate = (entity_id: number, year: number) =>
  api.GET("/biomethane/digestate/", {
    params: {
      query: {
        entity_id,
        year,
      },
    },
  })
