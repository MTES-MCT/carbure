import { EntityPreview, UploadCheckReportInfo } from "common/types"
import { ElecApplicationSample } from "elec-audit-admin/types"

export enum ElecAuditApplicationStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
  AuditInProgress = "AUDIT_IN_PROGRESS",
  AuditDone = "AUDIT_DONE",
}

export interface ElecChargePointsApplication {
  id: number
  cpo: EntityPreview
  station_count: number
  charge_point_count: number
  power_total: number
  application_date: string
  status: ElecAuditApplicationStatus
  validation_date?: string
  // audit_order_date?: string
}

export interface ElecChargePointsApplicationDetails
  extends ElecChargePointsApplication {
  email_contacts: string[]
  sample?: ElecApplicationSample
}

export interface ElecChargePointsSnapshot {
  station_count: number
  charge_point_count: number
  power_total: number
}

export interface ElecChargePointsApplicationCheckInfo
  extends UploadCheckReportInfo {
  charge_point_count: number
}

export interface ElecMeterReadingsApplicationDetails
  extends ElecMeterReadingsApplication {
  email_contacts: string[]
  power_total: number
  sample?: ElecApplicationSample
}

export enum MeterReadingsApplicationUrgencyStatus {
  Low = "LOW",
  High = "HIGH",
  Critical = "CRITICAL",
}

export interface ElecMeterReadingsCurrentApplicationsPeriod {
  year: number
  quarter: number
  urgency_status: MeterReadingsApplicationUrgencyStatus
  deadline: string
  charge_point_count: number
}
export interface ElecMeterReadingsApplicationsResponse {
  applications: ElecMeterReadingsApplication[]
  current_application?: ElecMeterReadingsApplication
  current_application_period: ElecMeterReadingsCurrentApplicationsPeriod
}

export interface ElecMeterReadingsApplication {
  id: number
  cpo: EntityPreview
  station_count: number
  charge_point_count: number
  energy_total: number
  year: number
  quarter: number
  application_date: string
  validation_date?: string
  status: ElecAuditApplicationStatus
}

export interface ElecMeterReadingsApplicationCheckInfo
  extends UploadCheckReportInfo {
  year: number
  quarter: number
  charge_point_count: number
}

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
  latest_meter_reading_date: string | null
  measure_energy: number
  installation_date: string
  status: ChargePointStatus
  is_article_2: boolean // If a charge point is NOT concerned by a reading meter
  latitude: number
  longitude: number
  nominal_power: number
  measure_reference_point_id: string // See more https://particulier.edf.fr/fr/accueil/aide-contact/faq/compteur/numero-prm.html
  initial_index: number
  initial_index_date: string
}

export type ElecMeter = {
  id: number
  charge_point: number
  initial_index: number
  initial_index_date: string
  mid_certificate: string
}
