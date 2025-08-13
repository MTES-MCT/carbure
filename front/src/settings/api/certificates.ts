import { api as apiFetch } from "common/services/api-fetch"
import { CertificateType } from "common/types"

export function getCertificates(query: string) {
  return apiFetch.GET("/resources/certificates", {
    params: { query: { query } },
  })
}

export function getMyCertificates(
  entity_id: number,
  production_site_id?: number
) {
  return apiFetch.GET("/entities/certificates/", {
    params: { query: { entity_id, production_site_id } },
  })
}

export function addCertificate(
  entity_id: number,
  certificate_id: string,
  certificate_type: CertificateType
) {
  return apiFetch.POST("/entities/certificates/add/", {
    params: { query: { entity_id } },
    body: {
      certificate_id: certificate_id,
      certificate_type: certificate_type,
    },
  })
}

export function deleteCertificate(
  entity_id: number,
  certificate_id: string,
  certificate_type: CertificateType
) {
  return apiFetch.POST("/entities/certificates/delete/", {
    params: { query: { entity_id } },
    body: {
      certificate_id: certificate_id,
      certificate_type: certificate_type,
    },
  })
}

export function updateCertificate(
  entity_id: number,
  old_certificate_id: string,
  old_certificate_type: CertificateType,
  new_certificate_id: string,
  new_certificate_type: CertificateType
) {
  return apiFetch.POST("/entities/certificates/update-certificate/", {
    params: { query: { entity_id } },
    body: {
      old_certificate_id,
      old_certificate_type,
      new_certificate_id,
      new_certificate_type,
    },
  })
}

export function setDefaultCertificate(
  entity_id: number,
  certificate_id: string
) {
  return apiFetch.POST("/entities/certificates/set-default/", {
    params: { query: { entity_id } },
    body: {
      certificate_id,
    },
  })
}
