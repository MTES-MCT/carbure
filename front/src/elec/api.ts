import { api, Api } from "common/services/api"
import { ElecSnapshot } from "./types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/elec/cpo/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecSnapshot>>("/v5/elec/cpo/snapshot", {
    params: { entity_id, year },
  })
}
