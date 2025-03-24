import { cpo } from "common/__test__/data"
import { UploadCheckError } from "common/types"
import {
  ElecAuditorApplication,
  ElecAuditorApplicationDetails,
  ElecAuditorApplicationsData,
  ElecAuditorApplicationsSnapshot,
  ElecAuditorApplicationsStatus,
  ElecAuditorUploadCheckReportInfo,
} from "elec-auditor/types"
import { elecAuditApplicationSample } from "elec/__test__/data"

export const elecAuditYears = [2024, 2023, 2020]
export const elecAuditSnapshot: ElecAuditorApplicationsSnapshot = {
  charge_points_applications_audit_done: 1,
  charge_points_applications_audit_in_progress: 1,
}

export const elecAuditCPOFilters = ["Aménageur 1", "Aménageur 2", "Aménageur 3"]

export const elecAuditorApplicationAuditInProgress: ElecAuditorApplication = {
  id: 3,
  cpo: cpo,
  station_count: 1,
  charge_point_count: 5,
  application_date: "2023-09-01",
  status: ElecAuditorApplicationsStatus.AuditInProgress,
  audit_order_date: "2023-09-26",
}
export const elecAuditorApplicationAuditDone: ElecAuditorApplication = {
  id: 3,
  cpo: cpo,
  station_count: 1,
  charge_point_count: 5,
  application_date: "2023-09-01",
  status: ElecAuditorApplicationsStatus.AuditDone,
  audit_order_date: "2023-09-26",
}

export const elecAuditChargePointsApplications: ElecAuditorApplication[] = [
  elecAuditorApplicationAuditInProgress,
  elecAuditorApplicationAuditDone,
]

export const elecAuditApplicationsList: ElecAuditorApplicationsData = {
  audit_applications: elecAuditChargePointsApplications,
  from: 0,
  ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
  returned: 10,
  total: 11,
}

export const elecAuditorApplicationDetailsInProgress: ElecAuditorApplicationDetails =
  {
    ...elecAuditorApplicationAuditInProgress,
    sample: elecAuditApplicationSample,
  }

const error: UploadCheckError = {
  line: 1,
  error: "NO_CHARGE_POINT_DETECTED",
}

export const elecAuditApplicationCheckReportError: ElecAuditorUploadCheckReportInfo =
  {
    errors: [error],
    file_name: "auditreport.xlsx",
    error_count: 1,
  }
export const elecAuditApplicationCheckReportSuccess: ElecAuditorUploadCheckReportInfo =
  {
    file_name: "auditreport.xlsx",
    error_count: 0,
  }
