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
