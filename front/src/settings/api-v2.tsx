import { api, Api } from "common-v2/services/api"
import { EntityCertificate, CertificateData, CertificateType } from "common/types"


export function getCertificates(query: string) {
  return api.get<Api<CertificateData[]>>("/get-certificates", {
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
      production_site_id
    }
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
  new_certificate_type: CertificateType,
) {
  return api.post("/update-certificate", {
    entity_id,
    old_certificate_id,
    old_certificate_type,
    new_certificate_id,
    new_certificate_type,
  })
}


export function setProductionSiteCertificates(
  entity_id: number,
  production_site_id: number,
  certificate_ids: string[]
) {
  return api.post("/set-production-site-certificates", {
    entity_id,
    production_site_id,
    certificate_ids,
  })
}

export function setDefaultCertificate(
  entity_id: number,
  certificate_id: string,
) {
  return api.post("/set-default-certificate", {
    entity_id,
    certificate_id,
  })
}