import { Entity, EntityType } from "carbure/types"
import { Order } from "common/components/table"
import { n } from "msw/lib/glossary-de6278a9"
import { ElecAdminProvisionCertificateFilterSelection } from "./components/provision-certificates/filters"

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


export interface ElecProvisionCertificatesData {
  elec_provision_certificates: ElecProvisionCertificatePreview[]
  from: number
  ids: number[]
  returned: number
  total: 7
}

export interface ElecProvisionCertificateCPOPreview {
  id: number,
  name: string,
  entity_type: EntityType
}
export interface ElecProvisionCertificatePreview {
  id: number
  cpo: ElecProvisionCertificateCPOPreview
  energy_amount: number
  operating_unit: string
  quarter: number
  remaining_energy_amount: number
  year: number
}