import { api } from "common/services/api-fetch"

export const getStations = (entity_id: number) =>
  api.GET("/h2/stations/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
