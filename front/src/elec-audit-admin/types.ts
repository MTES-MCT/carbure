import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { CBQueryParams, CBQueryStates, CBSnapshotType } from "common/hooks/query-builder"
import {
  ElecChargePointsApplication,
  ElecMeterReadingsApplication,
} from "elec/types"

export interface ElecAdminAuditSnapshot extends CBSnapshotType {
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


export interface ElecAdminAuditQuery extends CBQueryParams {
  [ElecAdminAuditFilter.Cpo]?: string[]
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

