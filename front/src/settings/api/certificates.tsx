import { api, Api } from "common/services/api"
import { Certificate, CertificateType, EntityCertificate } from "carbure/types"

export function getCertificates(query: string) {
  return api.get<Api<Certificate[]>>("/get-certificates", {
    params: { query },
  })
}

export function getMyCertificates(
  entity_id: number,
  production_site_id?: number
) {
  return api.get<Api<EntityCertificate[]>>("/get-my-certificates", {
    params: {
      entity_id,
      production_site_id,
    },
  })
}

export function addCertificate(
  entityID: number,
  certificate_id: string,
  certificate_type: CertificateType
) {
  return api.post("/add-certificate", {
    entity_id: entityID,
    certificate_id: certificate_id,
    certificate_type: certificate_type,
  })
}

export function deleteCertificate(
  entityID: number,
  certificate_id: string,
  certificate_type: CertificateType
) {
  return api.post("/delete-certificate", {
    entity_id: entityID,
    certificate_id: certificate_id,
    certificate_type: certificate_type,
  })
}

export function updateCertificate(
  entity_id: number,
  old_certificate_id: string,
  old_certificate_type: CertificateType,
  new_certificate_id: string,
  new_certificate_type: CertificateType
) {
  return api.post("/update-certificate", {
    entity_id,
    old_certificate_id,
    old_certificate_type,
    new_certificate_id,
    new_certificate_type,
  })
}

export function setDefaultCertificate(
  entity_id: number,
  certificate_id: string
) {
  return api.post("/set-default-certificate", {
    entity_id,
    certificate_id,
  })
}
