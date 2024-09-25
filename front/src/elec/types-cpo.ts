import { CBQueryParams, CBSnapshot } from "common/hooks/query-builder"
import {
  ElecProvisionCertificatePreview,
  ElecTransferCertificateFilter,
  ElecTransferCertificatePreview,
} from "./types"

export interface ElecCPOSnapshot extends CBSnapshot {
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

export enum ElecCPOProvisionCertificateFilter {
  Quarter = "quarter",
  OperatingUnit = "operating_unit",
}

export interface ElecCPOProvisionCertificateQuery extends CBQueryParams {
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

export enum ElecTransferCertificateStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
}

export interface ElecTransferCertificateQuery extends CBQueryParams {
  [ElecTransferCertificateFilter.Operator]?: string[]
  [ElecTransferCertificateFilter.Cpo]?: string[]
  [ElecTransferCertificateFilter.TransferDate]?: string[]
  [ElecTransferCertificateFilter.CertificateId]?: string[]
}
