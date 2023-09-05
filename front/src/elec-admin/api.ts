import { api, Api } from "common/services/api"
import { ElecAdminProvisionCertificateQuery, ElecAdminSnapshot } from "./types"

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
  return api.post("/v5/admin/elec/import-provision-certificates", {
    entity_id,
    file,
  })
}

export function getProvisionCertificates(query: ElecAdminProvisionCertificateQuery) {
  return api.get("/v5/admin/elec/provision-certificates", {
    params: query,
  })
}
