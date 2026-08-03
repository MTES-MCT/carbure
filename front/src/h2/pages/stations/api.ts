import { api } from "common/services/api-fetch"
import {
  H2StationFilter,
  H2StationInputRequest,
  H2StationsQuery,
} from "h2/types"

export function getH2Stations(query: H2StationsQuery) {
  return api.GET("/h2/stations/", {
    params: { query },
  })
}

export function createH2Station(
  entity_id: number,
  station: H2StationInputRequest
) {
  return api.POST("/h2/stations/", {
    params: { query: { entity_id } },
    body: station,
  })
}

export function updateH2Station(
  entity_id: number,
  station_id: number,
  station: H2StationInputRequest
) {
  return api.PATCH("/h2/stations/{id}/", {
    params: {
      query: { entity_id },
      path: { id: station_id },
    },
    body: station,
  })
}

export function getH2StationsFilters(
  filter: H2StationFilter,
  query: H2StationsQuery
) {
  return api
    .GET("/h2/stations/filters/", {
      params: { query: { filter, ...query } },
    })
    .then((res) => res.data ?? [])
}
