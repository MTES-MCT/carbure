import {
  ElecAdminAuditSnapshot,
  ElecChargePointsApplicationsData,
  ElecMeterReadingsApplicationsData,
} from "elec-audit-admin/types"
import {
  elecChargePointsApplications,
  elecMeterReadingsApplications,
} from "elec/__test__/data"

export const elecAdminAuditSnapshot: ElecAdminAuditSnapshot = {
  charge_points_applications: 2,
  charge_points_applications_pending: 1,
  charge_points_applications_history: 1,
  charge_points_applications_audit_in_progress: 1,
  charge_points_applications_audit_done: 1,
  meter_readings_applications: 2,
  meter_readings_applications_pending: 1,
  meter_readings_applications_history: 1,
  meter_readings_applications_audit_in_progress: 1,
  meter_readings_applications_audit_done: 1,
}

export const elecAdminChargePointsApplicationsList: ElecChargePointsApplicationsData =
  {
    charge_points_applications: elecChargePointsApplications,
    from: 0,
    ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
    returned: 10,
    total: 11,
  }

export const elecAdminMeterReadingsApplicationsList: ElecMeterReadingsApplicationsData =
  {
    meter_readings_applications: elecMeterReadingsApplications,
    from: 0,
    ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
    returned: 10,
    total: 11,
  }

export const elecAuditAdminMeterReadingsFilters: string[] = [
  "CPO Test",
  "Cpo Test 2",
]
