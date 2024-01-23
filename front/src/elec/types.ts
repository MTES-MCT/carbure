import { EntityPreview } from "carbure/types"
import {
  ElecCPOProvisionCertificateQuery,
  ElecTransferCertificateStatus,
} from "./types-cpo"

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

export const QUERY_RESET: Partial<ElecCPOProvisionCertificateQuery> = {
  limit: undefined,
  from_idx: undefined,
  sort_by: undefined,
  order: undefined,
}

export interface ElecTransferCertificatesDetails
  extends ElecTransferCertificatePreview {
  comment: string
}
export interface ElecProvisionCertificatesDetails
  extends ElecProvisionCertificatePreview { }

export enum ElecChargePointsApplicationStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
}

export interface ElecChargePointsApplication {
  id: number
  cpo: EntityPreview
  station_count: number
  charge_point_count: number
  power_total: number
  application_date: string
  validation_date?: string
  status: ElecChargePointsApplicationStatus
}
export interface ElecChargePointsSnapshot {
  station_count: number
  charge_point_count: number
  power_total: number
}

export interface ElecChargePointsApplicationCheckInfo {
  errors?: ChargePointsApplicationError[]
  file_name: string
  error_count: number
  charge_point_count: number
  pending_application_already_exists?: boolean
}

export interface ChargePointsApplicationError {
  line: number
  error: string
  meta?: null | any
}

// METER READINGS

export enum ElecMeterReadingsApplicationStatus {
  Pending = "PENDING",
  Accepted = "ACCEPTED",
  Rejected = "REJECTED",
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
  status: ElecMeterReadingsApplicationStatus
}

export interface ElecMeterReadingsApplicationCheckInfo {
  errors?: MeterReadingsApplicationError[]
  file_name: string
  error_count: number
  year: number
  quarter: number
  charge_point_count: number
  pending_application_already_exists?: boolean
}

export interface MeterReadingsApplicationError {
  line: number
  error: string
  meta?: null | any
}
