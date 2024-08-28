import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { CBQueryStates, CBSnapshot } from "common/hooks/query-builder"

export interface ElecAdminSnapshot extends CBSnapshot {
  provision_certificates: number
  provision_certificates_available: number
  provision_certificates_history: number
  transfer_certificates_pending: number
  transfer_certificates_accepted: number
  transfer_certificates_rejected: number
  transfer_certificates: number
  provisioned_energy: number
  transferred_energy: number
}

export enum ElecAdminProvisionCertificateStatus {
  Available = "AVAILABLE",
  History = "HISTORY",
}

export type ElecAdminProvisionCertificateFilterSelection = Partial<
  Record<ElecAdminProvisionCertificateFilter, string[]>
>

export interface ElecAdminProvisionCertificateStates extends CBQueryStates {
  status: ElecAdminProvisionCertificateStatus
  filters: ElecAdminProvisionCertificateFilterSelection
  snapshot?: ElecAdminSnapshot
}

export enum ElecAdminProvisionCertificateFilter {
  Quarter = "quarter",
  OperatingUnit = "operating_unit",
  Cpo = "cpo",
}

export interface ElecAdminProvisionCertificateQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  sort_by?: string
  order?: string
  from_idx?: number
  limit?: number
  [ElecAdminProvisionCertificateFilter.Cpo]?: string[]
  [ElecAdminProvisionCertificateFilter.OperatingUnit]?: string[]
  [ElecAdminProvisionCertificateFilter.Quarter]?: string[]
}

// TRANSFER

export enum ElecAdminTransferCertificateFilter {
  TransferDate = "transfer_date",
  Cpo = "cpo",
  Operator = "operator",
  CertificateId = "certificate_id",
}
export interface ElecAdminTransferCertificateQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  sort_by?: string
  order?: string
  from_idx?: number
  limit?: number
  [ElecAdminProvisionCertificateFilter.Cpo]?: string[]
  [ElecAdminProvisionCertificateFilter.OperatingUnit]?: string[]
  [ElecAdminProvisionCertificateFilter.Quarter]?: string[]
}

export type ElecAdminTransferCertificateFilterSelection = Partial<
  Record<ElecAdminTransferCertificateFilter, string[]>
>

export interface ElecAdminTransferCertificateStates {
  entity: Entity
  year: number
  filters: ElecAdminTransferCertificateFilterSelection
  search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecAdminSnapshot
}
