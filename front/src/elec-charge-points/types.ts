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
  charge_point_id: string
  station_id: number
  mid_id: string
  current_type?: ChargePointType
  measure_date: string | null
  measure_energy: number
  installation_date: string
  status: ChargePointStatus
  is_article_2: boolean // If a charge point is NOT concerned by a reading meter
  latitude: number
  longitude: number
  nominal_power: number
  measure_reference_point_id: string // See more https://particulier.edf.fr/fr/accueil/aide-contact/faq/compteur/numero-prm.html
}

export type ElecMeter = {
  id: number
  charge_point: number
  initial_index: number
  initial_index_date: string
  mid_certificate: string
}
