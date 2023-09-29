import { EntityPreview } from "carbure/types"
import { ElecCPOTransferCertificateStatus } from "./types-cpo"

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


export interface ElecTransferCertificatesData {
  elec_provision_certificates: ElecTransferCertificatePreview[]
  from: number
  ids: number[]
  returned: number
  total: number
}
