import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { ElecChargePointsApplication } from "elec/types"

export interface ElecAdminAuditSnapshot {
  charge_points_applications: number
  charge_points_applications_pending: number
  charge_points_applications_history: number
  meter_readings_applications: number
  meter_readings_applications_pending: number
  meter_readings_applications_history: number
}

export enum ElecAdminAuditFilter {
  Period = "period",
  Cpo = "cpo",
}

export enum ElecAdminAuditStatus {
  Pending = "PENDING",
  History = "HISTORY",
}

export type ElecAdminAuditFilterSelection = Partial<Record<ElecAdminAuditFilter, string[]>>

export interface ElecChargePointsApplicationsData {
  charge_points_applications: ElecChargePointsApplication[]
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
