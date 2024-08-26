import { EntityPreview, UploadCheckReportInfo } from "carbure/types"
import {
  ElecCPOProvisionCertificateQuery,
  ElecTransferCertificateStatus,
} from "./types-cpo"
import { ElecApplicationSample } from "elec-audit-admin/types"

export interface ElecProvisionCertificatePreview {
  id: number
  cpo: EntityPreview
  energy_amount: number
  operating_unit: string
  quarter: number
  remaining_energy_amount: number
  current_type: string
  year: number
}
export interface ElecTransferCertificatePreview {
  id: number
  supplier: EntityPreview
  client: EntityPreview
  transfer_date: string
  energy_amount: number
  status: ElecTransferCertificateStatus
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


export interface ElecTransferCertificatesDetails
  extends ElecTransferCertificatePreview {
  comment: string
}
export type ElecProvisionCertificatesDetails = ElecProvisionCertificatePreview

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

export interface ElecChargePointsApplicationDetails extends ElecChargePointsApplication {
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
