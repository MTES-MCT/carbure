import { api } from "common/services/api-fetch"
import { ProvisionCertificatesQuery, TransferCertificatesQuery } from "./types"

export function getYears(entity_id: number) {
  return api.GET("/elec-v2/certificates/years/", {
    params: { query: { entity_id } },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.GET("/elec-v2/certificates/snapshot/", {
    params: { query: { entity_id, year } },
  })
}

export function getClients(entity_id: number, query: string) {
  return api
    .GET("/elec-v2/certificates/clients/", {
      params: { query: { entity_id, query } },
    })
    .then((res) => res.data ?? [])
}

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

export function getProvisionCertificateBalance(entity_id: number) {
  return api.GET("/elec-v2/provision-certificates/balance/", {
    params: { query: { entity_id } },
  })
}

export function createTransferCertificate(
  entity_id: number,
  energy_amount: number,
  client: number
) {
  return api.POST("/elec-v2/provision-certificates/transfer/", {
    params: { query: { entity_id } },
    body: { energy_amount, client },
  })
}

export function getTransferCertificates(query: TransferCertificatesQuery) {
  return api.GET("/elec-v2/transfer-certificates/", {
    params: { query },
  })
}

export function getTransferCertificateFilters(
  filter: string,
  query: TransferCertificatesQuery
) {
  return api
    .GET("/elec-v2/transfer-certificates/filters/", {
      params: { query: { ...query, filter } },
    })
    .then((res) => res.data ?? [])
}

export function getTransferCertificateDetails(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.GET("/elec-v2/transfer-certificates/{id}/", {
    params: {
      path: { id: transfer_certificate_id },
      query: { entity_id },
    },
  })
}
