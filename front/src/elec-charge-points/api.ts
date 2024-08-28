import { api, Api } from "common/services/api"
import {
  ChargePointsListData,
  ChargePointsListQuery,
  ChargePointsSnapshot,
} from "./types-charge-points"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/cpo/charge-point-years", {
    params: { entity_id },
  })
}

export function getChargePointsSnapshot(entity_id: number, year: number) {
  return api.get<Api<ChargePointsSnapshot>>("/elec/cpo/charge-point-snapshot", {
    params: { entity_id, year, category: "charge_point" },
  })
}

export function getChargePointsList(query: ChargePointsListQuery) {
  return api.get<Api<ChargePointsListData>>("elec/charge-points", {
    params: query,
  })
}
