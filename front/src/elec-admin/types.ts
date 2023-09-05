import { Entity } from "carbure/types"
import { Order } from "common/components/table"

export interface ElecAdminSnapshot {
  provision_certificates: number
  transfer_certificates: number
  provided_energy: number
  transfered_energy: number
}


export enum ElecAdminProvisionCertificateStatus {
  Available = "AVAILABLE",
  History = "HISTORY",
}

export interface ElecAdminProvisionCertificateStates {
  //old QueryParams
  entity: Entity
  year: number
  status: ElecAdminProvisionCertificateStatus
  // filters: SafFilterSelection
  search?: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecAdminSnapshot
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
  // [SafFilter.Feedstocks]?: string[]
  // [SafFilter.Periods]?: string[]
  // [SafFilter.Clients]?: string[]
}

