import { CBSnapshot } from "common/hooks/query-builder"

export interface ElecOperatorSnapshot extends CBSnapshot {
  transfer_cert_pending: number
  transfer_cert_accepted: number
  acquired_energy: number
}

export enum ElecOperatorStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
}
