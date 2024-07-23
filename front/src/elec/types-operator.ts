export interface ElecOperatorSnapshot {
  transfer_cert_pending: number
  transfer_cert_accepted: number
  acquired_energy: number
}

export enum ElecOperatorStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
}
