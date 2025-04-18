import { Entity } from "common/types"
import { Order } from "common/components/table"
import { ElecAdminSnapshot } from "elec-admin/types"

export enum ElecAdminProvisionCertificateStatus {
  Available = "AVAILABLE",
  History = "HISTORY",
}

export type ElecAdminProvisionCertificateFilterSelection = Partial<
  Record<ElecAdminProvisionCertificateFilter, string[]>
>

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
