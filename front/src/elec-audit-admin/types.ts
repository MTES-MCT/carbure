import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import {
  ElecChargePointsApplication,
  ElecMeterReadingsApplication,
} from "elec/types"

export interface ElecAdminAuditSnapshot {
  charge_points_applications_audit_done: number
  charge_points_applications_audit_in_progress: number
  charge_points_applications_history: number
  charge_points_applications_pending: number
  charge_points_applications: number
  meter_readings_applications_history: number
  meter_readings_applications_audit_done: number
  meter_readings_applications_pending: number
  meter_readings_applications_audit_in_progress: number
  meter_readings_applications: number
}

export enum ElecAdminAuditFilter {
  Quarter = "quarter",
  Cpo = "cpo",
}

export enum ElecAdminAuditStatus {
  Pending = "PENDING",
  AuditInProgress = "AUDIT_IN_PROGRESS",
  AuditDone = "AUDIT_DONE",
  History = "HISTORY",
}

export type ElecAdminAuditFilterSelection = Partial<
  Record<ElecAdminAuditFilter, string[]>
>

export interface ElecChargePointsApplicationsData {
  charge_points_applications: ElecChargePointsApplication[]
  from: number
  ids: number[]
  returned: number
  total: number
}

export interface ElecChargePointPreview {
  charge_point_id: string
  longitude: number
  latitude: number
}
export interface ElecApplicationSample {
  application_id: number
  percentage: number
  charge_points: ElecChargePointPreview[]
  comment_count?: number
  auditor_name?: string
}

export interface ElecMeterReadingsApplicationsData {
  meter_readings_applications: ElecMeterReadingsApplication[]
  from: number
  ids: number[]
  returned: number
  total: number
}

export interface ElecAdminAuditQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  sort_by?: string
  order?: string
  from_idx?: number
  limit?: number
  [ElecAdminAuditFilter.Cpo]?: string[]
  // [ElecAdminAuditFilter.Period]?: string[]
}

export interface ElecAdminAuditStates {
  entity: Entity
  year: number
  filters: ElecAdminAuditFilterSelection
  search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecAdminAuditSnapshot
}
