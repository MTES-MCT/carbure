import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { ElecAdminSnapshot } from "elec-admin/types"
import { ElecAdminProvisionCertificateFilter } from "../provision-certificates/types"


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
