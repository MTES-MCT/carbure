import { api, Api } from "common/services/api"
import { ElecCPOSnapshot } from "./types-cpo"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/elec/operator/years", { params: { entity_id } })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecCPOSnapshot>>("/v5/elec/operator/snapshot", {
    params: { entity_id, year },
  })
}
