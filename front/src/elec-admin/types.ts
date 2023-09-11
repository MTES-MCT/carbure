import { Entity } from "carbure/types"
import { Order } from "common/components/table"

export interface ElecAdminSnapshot {
  provision_certificates: number
  transfer_certificates: number
  provisioned_energy: number
  transferred_energy: number
}


export enum ElecAdminProvisionCertificateStatus {
  Available = "AVAILABLE",
  History = "HISTORY",
}

export type ElecAdminProvisionCertificateFilterSelection = Partial<Record<ElecAdminProvisionCertificateFilter, string[]>>

export interface ElecAdminProvisionCertificateStates {
  entity: Entity
  year: number
  status: ElecAdminProvisionCertificateStatus
  filters: ElecAdminProvisionCertificateFilterSelection
  search?: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
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

