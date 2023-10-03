import { EntityPreview } from "carbure/types"
import {
  ElecCPOProvisionCertificateQuery,
  ElecCPOTransferCertificateStatus,
} from "./types-cpo"
import { ElecOperatorStatus } from "./types-operator"

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
  status: ElecCPOTransferCertificateStatus | ElecOperatorStatus
  certificate_id: number
}

export interface ElecTransferCertificate
  extends ElecTransferCertificatePreview {
  comment: string
}

export interface ElecTransferCertificatesData {
  elec_transfer_certificates: ElecTransferCertificatePreview[]
  from: number
  ids: number[]
  returned: number
  total: number
}

export enum ElecTransferCertificateFilter {
  TransferDate = "transfer_date",
  Operator = "operator",
  Cpo = "cpo",
  CertificateId = "certificate_id",
}

export const QUERY_RESET: Partial<ElecCPOProvisionCertificateQuery> = {
  limit: undefined,
  from_idx: undefined,
  sort_by: undefined,
  order: undefined,
}

export interface ElecTransferCertificatesDetails extends ElecTransferCertificatePreview {
  comment: string
}
export interface ElecProvisionCertificatesDetails extends ElecProvisionCertificatePreview {

}