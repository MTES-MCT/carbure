export type ChargePointsSnapshot = {
  charge_point_applications: number
  meter_reading_applications: number
  charge_points: number

  // Data used for status tab in "charge points" page
  pending: number
  audit_in_progress: number
  accepted: number
}

export enum ChargePointStatus {
  Pending = "PENDING",
  AuditInProgress = "AUDIT_IN_PROGRESS",
  Accepted = "ACCEPTED",
}

export enum ChargePointType {
  AC = "AC", // courant alternatif
  DC = "DC", // courant continu
}

export type ChargePoint = {
  id: number
  application_date?: string
  charge_point_id: number
  station_id: number
  current_type?: ChargePointType
  measure_date: string | null
  measure_energy: number
  installation_date: string
  status: ChargePointStatus
  is_article_2: boolean // If a charge point is NOT concerned by a reading meter
}
