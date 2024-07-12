import { Entity, EntityPreview } from "carbure/types"
import { Order } from "common/components/table"
import { ElecApplicationSample } from "elec-audit-admin/types"
import { UploadCheckError } from "elec/types"

export interface ElecAuditSnapshot {
  charge_points_applications_audit_in_progress: number
  charge_points_applications_audit_done: number
}

export enum ElecAuditFilter {
  Cpo = "cpo",
}

export enum ElecAuditStatus {
  AuditInProgress = "IN_PROGRESS",
  AuditDone = "AUDITED",
}

export type ElecAuditFilterSelection = Partial<Record<ElecAuditFilter, string[]>>


export interface ElecAuditApplicationsData {
  audit_applications: ElecAuditApplication[]
  from: number
  ids: number[]
  returned: number
  total: number
}
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

export interface ElecAuditApplication {
  id: number
  cpo: EntityPreview
  station_count: number
  charge_point_count: number
  // power_total: number
  application_date: string
  status: ElecAuditStatus
  // validation_date?: string
  audit_order_date?: string
}


export interface ElecAuditApplicationDetails extends ElecAuditApplication {
  sample?: ElecApplicationSample
}


export interface ElecAuditReportInfo {
  errors?: UploadCheckError[]
  file_name: string
  error_count: number
}