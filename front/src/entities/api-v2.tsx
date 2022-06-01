import api, { Api } from "common-v2/services/api"
import { EntityCertificate } from "common-v2/types"
import { EntityDetails } from "./api"

export function getEntityCertificates(entity_id?: number) {
  return api.get<Api<EntityCertificate[]>>("/admin/entity-certificates", {
    params: { entity_id },
  })
}

export function checkEntityCertificate(entity_certificate_id: number) {
  return api.post("admin/entity-certificates/check", { entity_certificate_id })
}

export function rejectEntityCertificate(entity_certificate_id: number) {
  return api.post("admin/entity-certificates/reject", { entity_certificate_id })
}

export function getEntities() {
  return api.get<Api<EntityDetails[]>>("/v3/admin/entities")
}
