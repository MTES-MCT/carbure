import { api, Api } from "common/services/api"
import { ElecAdminSnapshot } from "./types"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/v5/admin/elec/years", {
    params: { entity_id },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.get<Api<ElecAdminSnapshot>>("/v5/admin/elec/snapshot", {
    params: { entity_id, year },
  })
}

export function importProvisionCertificates(entity_id: number, file: File) {
  console.log('entity_id:', entity_id)
  return api.post("/v5/admin/elec/import-provision-certificates", {
    entity_id,
    file,
  })
}
