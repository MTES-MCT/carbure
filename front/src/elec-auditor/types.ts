import { Entity, EntityPreview, UploadCheckReportInfo } from "carbure/types"
import { Order } from "common/components/table"
import { CBQueryParams, CBSnapshot } from "common/hooks/query-builder"
import { ElecApplicationSample } from "elec-audit-admin/types"

export interface ElecAuditorApplicationsSnapshot extends CBSnapshot {
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


export interface ElecAuditorApplicationsData {
  audit_applications: ElecAuditorApplication[]
  from: number
  ids: number[]
  returned: number
  total: number
}
export interface ElecAuditorApplicationsQuery extends CBQueryParams {
  [ElecAuditorApplicationsFilter.Cpo]?: string[]
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


