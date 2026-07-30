import { api } from "common/services/api-fetch"
import { H2StationInputRequest } from "h2/types"

export function getStations(entity_id: number) {
  return api.GET("/h2/stations/", {
    params: { query: { entity_id } },
  })
}
export function createStation(
  station: H2StationInputRequest,
  entity_id: number
) {
  return api.POST("/h2/stations/", {
    params: { query: { entity_id } },
    body: station,
  })
}
