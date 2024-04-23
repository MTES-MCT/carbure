import { ElecAdminAuditSnapshot, ElecChargePointsApplicationSample, ElecChargePointsApplicationsData, ElecMeterReadingsApplicationsData } from "elec-audit-admin/types";
import { elecChargePointsApplications, elecMeterReadingsApplications } from "elec/__test__/data";

export const elecAdminAuditSnapshot: ElecAdminAuditSnapshot = {
  charge_points_applications: 2,
  charge_points_applications_pending: 1,
  charge_points_applications_history: 1,
  charge_points_applications_audit_done: 1,
  charge_points_applications_audit_in_progress: 1,
  meter_readings_applications: 2,
  meter_readings_applications_pending: 1,
  meter_readings_applications_history: 1,
}

export const elecAdminChargePointsApplicationsList: ElecChargePointsApplicationsData = {
  charge_points_applications: elecChargePointsApplications,
  from: 0,
  ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
  returned: 10,
  total: 11
}


export const elecAdminMeterReadingsApplicationsList: ElecMeterReadingsApplicationsData = {
  meter_readings_applications: elecMeterReadingsApplications,
  from: 0,
  ids: [1, 2, 3, 4, 13, 14, 15, 22, 23, 24, 25],
  returned: 10,
  total: 11
}

export const elecChargePointsApplicationSample: ElecChargePointsApplicationSample = {
  application_id: 1,
  percentage: 10,
  charge_points: [
    {
      charge_point_id: "FR000028067822",
      longitude: 5.143766000000000,
      latitude: 43.329200000000000
    },
    {
      charge_point_id: "FR000012616553",
      longitude: 43.476584000000000,
      latitude: 5.476711000000000
    }
  ]
}
