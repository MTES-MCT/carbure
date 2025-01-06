import { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { CertificateType, EntityCertificate } from "carbure/types"

export function getCertificates(query: string) {
  return apiFetch.GET("/resources/certificates", {
    params: { query: { query } },
  })
}

export function getMyCertificates(
  entity_id: number,
  production_site_id?: number
) {
  console.log("OKOKOKOKOK 40 empty array")
  return apiFetch.GET("/entities/certificates/", {
    params: { query: { entity_id, production_site_id } },
  })
}

export function addCertificate(
  entity_id: number,
  certificate_id: string,
  certificate_type: CertificateType
) {
  console.log("VERYUNSURE 41")
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
  console.log("VERYUNSURE 42")
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
  console.log("VERYUNSURE 43")
  return apiFetch.POST("/entities/certificates/update/", {
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
  console.log("VERYUNSURE 44")
  return apiFetch.POST("/entities/certificates/set-default/", {
    params: { query: { entity_id } },
    body: {
      certificate_id,
    },
  })
}
