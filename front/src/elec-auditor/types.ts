import { Entity, EntityPreview, UploadCheckError, UploadCheckReportInfo } from "carbure/types"
import { Order } from "common/components/table"
import { ElecApplicationSample } from "elec-audit-admin/types"

export interface ElecAuditorApplicationsSnapshot {
  charge_points_applications_audit_in_progress: number
  charge_points_applications_audit_done: number
}

export enum ElecAuditorApplicationsFilter {
  Cpo = "cpo",
}

export enum ElecAuditorApplicationsStatus {
  AuditInProgress = "IN_PROGRESS",
  AuditDone = "AUDITED",
}

export interface ElecAuditorUploadCheckReportInfo extends UploadCheckReportInfo {
  comment_count?: number
}


export type ElecAuditorApplicationsFilterSelection = Partial<Record<ElecAuditorApplicationsFilter, string[]>>


export interface ElecAuditorApplicationsData {
  audit_applications: ElecAuditorApplication[]
  from: number
  ids: number[]
  returned: number
  total: number
}
export interface ElecAuditorApplicationsQuery {
  entity_id: number
  status?: string
  year?: number
  from_idx?: number
  limit?: number
  [ElecAuditorApplicationsFilter.Cpo]?: string[]
}

export interface ElecAuditorApplicationsStates {
  entity: Entity
  year: number
  filters: ElecAuditorApplicationsFilterSelection
  // search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: ElecAuditorApplicationsSnapshot
}

export interface ElecAuditorApplication {
  id: number
  cpo: EntityPreview
  station_count: number
  charge_point_count: number
  // power_total: number
  application_date: string
  status: ElecAuditorApplicationsStatus
  // validation_date?: string
  audit_order_date?: string
}


export interface ElecAuditorApplicationDetails extends ElecAuditorApplication {
  sample?: ElecApplicationSample
}


