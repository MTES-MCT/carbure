import { ElecAdminAuditSnapshot, ElecApplicationSample, ElecChargePointsApplicationsData, ElecMeterReadingsApplicationsData } from "elec-audit-admin/types";
import { ElecAuditSnapshot } from "elec-audit/types";
import { elecChargePointApplicationAuditDone, elecChargePointApplicationAuditInProgress, elecChargePointsApplications, elecMeterReadingsApplications } from "elec/__test__/data";
import { ElecChargePointsApplication } from "elec/types";


export const elecAuditYears = [2024, 2023, 2020]
export const elecAuditSnapshot: ElecAuditSnapshot = {
  charge_points_applications_audit_done: 1,
  charge_points_applications_audit_in_progress: 1,
}

export const elecAuditCPOFilters = ["Aménageur 1", "Aménageur 2", "Aménageur 3"]


export const elecAuditChargePointsApplications: ElecChargePointsApplication[] = [
  elecChargePointApplicationAuditInProgress,
  elecChargePointApplicationAuditDone,
]

export const elecAuditChargePointsApplicationsList: ElecChargePointsApplicationsData = {
  charge_points_applications: elecAuditChargePointsApplications,
  from: 0,
  ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
  returned: 10,
  total: 11
}


