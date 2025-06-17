import { api } from "common/services/api-fetch"
import { ProvisionCertificatesQuery } from "./types"

export function getProvisionCertificates(query: ProvisionCertificatesQuery) {
  return api.GET("/elec-v2/provision-certificates/", {
    params: { query },
  })
}

export function getProvisionCertificateFilters(
  filter: string,
  query: ProvisionCertificatesQuery
) {
  return api
    .GET("/elec-v2/provision-certificates/filters/", {
      params: { query: { ...query, filter } },
    })
    .then((res) => res.data ?? [])
}

export function getProvisionCertificateDetails(
  entity_id: number,
  provision_certificate_id: number
) {
  return api.GET("/elec-v2/provision-certificates/{id}/", {
    params: {
      path: { id: provision_certificate_id },
      query: { entity_id },
    },
  })
}
