import api, { Api } from "common-v2/services/api"
import { EntityCertificate } from "common/types"

export function getEntityCertificates(entity_id?: number) {
  return api.get<Api<EntityCertificate[]>>("/admin/entity-certificates", {
    params: { entity_id },
  })
}

export function checkEntityCertificate(entity_certificate_id: number) {
  return api.post("admin/entity-certificates/check", { entity_certificate_id })
}
