import { api, download } from "common/services/api-fetch"
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

export function importProvisionCertificates(entity_id: number, file: File) {
  return api.POST("/elec-v2/provision-certificates/import/", {
    params: { query: { entity_id } },
    body: { file },
  })
}

export function getProvisionCertificates(query: ProvisionCertificatesQuery) {
  return api.GET("/elec-v2/provision-certificates/", {
    params: { query },
  })
}

export function exportProvisionCertificates(query: ProvisionCertificatesQuery) {
  return download("/elec-v2/provision-certificates/export/", query)
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

export function exportTransferCertificates(query: TransferCertificatesQuery) {
  return download("/elec-v2/transfer-certificates/export/", query)
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

export function acceptTransferCertificate(
  entity_id: number,
  transfer_certificate_id: number,
  used_in_tiruert: string,
  consumption_date?: string
) {
  return api.POST("/elec-v2/transfer-certificates/{id}/accept/", {
    params: {
      query: { entity_id },
      path: { id: transfer_certificate_id },
    },
    body: {
      consumption_date,
      used_in_tiruert,
    },
  })
}

export function rejectTransferCertificate(
  entity_id: number,
  transfer_certificate_id: number,
  comment: string
) {
  return api.POST("/elec-v2/transfer-certificates/{id}/reject/", {
    params: {
      query: { entity_id },
      path: { id: transfer_certificate_id },
    },
    body: { comment },
  })
}

export function cancelTransferCertificate(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.POST("/elec-v2/transfer-certificates/{id}/cancel/", {
    params: {
      query: { entity_id },
      path: { id: transfer_certificate_id },
    },
  })
}
