import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { ElecChargePointsApplication, ElecMeterReadingsApplication } from "elec/types"

export interface ElecAuditSnapshot {
  charge_points_applications_audit_in_progress: number
  charge_points_applications_audit_done: number
}

export enum ElecAuditFilter {
  Cpo = "cpo",
}

export enum ElecAuditStatus {
  AuditInProgress = "AUDIT_IN_PROGRESS",
  AuditDone = "AUDIT_DONE",
}

export type ElecAuditFilterSelection = Partial<Record<ElecAuditFilter, string[]>>



export interface ElecAuditQuery {
  entity_id: number
  status?: string
  year?: number
  search?: string
  sort_by?: string
  order?: string
  from_idx?: number
  limit?: number
  [ElecAuditFilter.Cpo]?: string[]
}

export interface ElecAuditStates {
  entity: Entity
  year: number
  filters: ElecAuditFilterSelection
  search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecAuditSnapshot
}


