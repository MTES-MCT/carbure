import { api, download } from "common/services/api-fetch"
import {
  ProvisionCertificatesQuery,
  TransferCertificateFilter,
  TransferCertificatesQuery,
  ProvisionCertificateFilter,
} from "./types"

export function getYears(entity_id: number) {
  return api.GET("/elec/certificates/years/", {
    params: { query: { entity_id } },
  })
}

export function getSnapshot(entity_id: number, year: number) {
  return api.GET("/elec/certificates/snapshot/", {
    params: { query: { entity_id, year } },
  })
}

export function getClients(entity_id: number, query: string) {
  return api
    .GET("/elec/certificates/clients/", {
      params: { query: { entity_id, query } },
    })
    .then((res) => res.data ?? [])
}

export function importProvisionCertificates(entity_id: number, file: File) {
  return api.POST("/elec/provision-certificates/import/", {
    params: { query: { entity_id } },
    body: { file },
  })
}

export function getProvisionCertificates(query: ProvisionCertificatesQuery) {
  return api.GET("/elec/provision-certificates/", {
    params: { query },
  })
}

export function exportProvisionCertificates(query: ProvisionCertificatesQuery) {
  return download("/elec/provision-certificates/export/", query)
}

export function getProvisionCertificateFilters(
  filter: ProvisionCertificateFilter,
  query: ProvisionCertificatesQuery
) {
  return api
    .GET("/elec/provision-certificates/filters/", {
      params: { query: { ...query, filter } },
    })
    .then((res) => res.data ?? [])
}

export function getProvisionCertificateDetails(
  entity_id: number,
  provision_certificate_id: number
) {
  return api.GET("/elec/provision-certificates/{id}/", {
    params: {
      path: { id: provision_certificate_id },
      query: { entity_id },
    },
  })
}

export function getProvisionCertificateBalance(entity_id: number) {
  return api.GET("/elec/provision-certificates/balance/", {
    params: { query: { entity_id } },
  })
}

export function createTransferCertificate(
  entity_id: number,
  energy_amount: number,
  client: number
) {
  return api.POST("/elec/provision-certificates/transfer/", {
    params: { query: { entity_id } },
    body: { energy_amount, client },
  })
}

export function getTransferCertificates(query: TransferCertificatesQuery) {
  return api.GET("/elec/transfer-certificates/", {
    params: { query },
  })
}

export function exportTransferCertificates(query: TransferCertificatesQuery) {
  return download("/elec/transfer-certificates/export/", query)
}

export function getTransferCertificateFilters(
  filter: TransferCertificateFilter,
  query: TransferCertificatesQuery
) {
  return api
    .GET("/elec/transfer-certificates/filters/", {
      params: { query: { ...query, filter } },
    })
    .then((res) => res.data ?? [])
}

export function getTransferCertificateDetails(
  entity_id: number,
  transfer_certificate_id: number
) {
  return api.GET("/elec/transfer-certificates/{id}/", {
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
  return api.POST("/elec/transfer-certificates/{id}/accept/", {
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
  return api.POST("/elec/transfer-certificates/{id}/reject/", {
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
  return api.POST("/elec/transfer-certificates/{id}/cancel/", {
    params: {
      query: { entity_id },
      path: { id: transfer_certificate_id },
    },
  })
}
