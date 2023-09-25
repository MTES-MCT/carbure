import { Entity, EntityPreview, EntityType } from "carbure/types"
import { Order } from "common/components/table"

export interface ElecCPOSnapshot {
  provisioned_energy: number
  remaining_energy: number
  provision_certificates_available: number
  provision_certificates_history: number
  transferred_energy: number
  transfer_certificates_pending: number
  transfer_certificates_accepted: number
  transfer_certificates_rejected: number
}



export enum ElecCPOProvisionCertificateStatus {
  Available = "AVAILABLE",
  History = "HISTORY",
}

export type ElecCPOProvisionCertificateFilterSelection = Partial<Record<ElecCPOProvisionCertificateFilter, string[]>>

export interface ElecCPOProvisionCertificateStates {
  entity: Entity
  year: number
  status: ElecCPOProvisionCertificateStatus
  filters: ElecCPOProvisionCertificateFilterSelection
  search?: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecCPOSnapshot
}

export enum ElecCPOProvisionCertificateFilter {
  Quarter = "quarter",
  OperatingUnit = "operating_unit",
}

export interface ElecCPOProvisionCertificateQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  sort_by?: string
  order?: string
  from_idx?: number
  limit?: number
  [ElecCPOProvisionCertificateFilter.OperatingUnit]?: string[]
  [ElecCPOProvisionCertificateFilter.Quarter]?: string[]
}



export interface ElecProvisionCertificatesData {
  elec_provision_certificates: ElecProvisionCertificatePreview[]
  from: number
  ids: number[]
  returned: number
  total: number
}
export interface ElecTransferCertificatesData {
  elec_transfer_certificates: ElecTransferCertificatePreview[]
  from: number
  ids: number[]
  returned: number
  total: number
}


export interface ElecProvisionCertificatePreview {
  id: number
  cpo: EntityPreview
  energy_amount: number
  operating_unit: string
  quarter: number
  remaining_energy_amount: number
  year: number
}
export interface ElecTransferCertificatePreview {
  id: number
  supplier: EntityPreview
  client: EntityPreview
  transfer_date: string
  energy_amount: number
  status: ElecCPOTransferCertificateStatus
  certificate_id: number
}


export enum ElecCPOTransferCertificateStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
}

export enum ElecCPOTransferCertificateFilter {
  TransferDate = "transfer_date",
  Operator = "operator",
  CertificateId = "certificate_id",
}
export interface ElecCPOTransferCertificateQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  sort_by?: string
  order?: string
  from_idx?: number
  limit?: number
  [ElecCPOProvisionCertificateFilter.OperatingUnit]?: string[]
  [ElecCPOProvisionCertificateFilter.Quarter]?: string[]
}



export interface ElecTransferCertificatesData {
  elec_provision_certificates: ElecTransferCertificatePreview[]
  from: number
  ids: number[]
  returned: number
  total: number
}

export type ElecCPOTransferCertificateFilterSelection = Partial<Record<ElecCPOTransferCertificateFilter, string[]>>

export interface ElecCPOTransferCertificateStates {
  entity: Entity
  year: number
  status: ElecCPOTransferCertificateStatus
  filters: ElecCPOTransferCertificateFilterSelection
  search?: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecCPOSnapshot
}