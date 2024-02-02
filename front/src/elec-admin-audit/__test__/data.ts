import { cpo } from "carbure/__test__/data";
import { EntityPreview, EntityType } from "carbure/types";
import { ElecAdminAuditSnapshot, ElecChargePointsApplicationsData } from "elec-admin-audit/types";
import { elecChargePointsApplications } from "elec/__test__/data";
import { ChargePointsApplicationError, ElecChargePointsApplication, ElecChargePointsApplicationCheckInfo, ElecChargePointsApplicationStatus, ElecMeterReadingsApplication, ElecMeterReadingsApplicationCheckInfo, ElecMeterReadingsApplicationStatus, ElecProvisionCertificatePreview, MeterReadingsApplicationError } from "elec/types";
import { ElecCPOSnapshot, ElecProvisionCertificatesData } from "elec/types-cpo";

export const elecAdminAuditSnapshot: ElecAdminAuditSnapshot = {
  charge_points_applications: 2,
  charge_points_applications_pending: 1,
  charge_points_applications_history: 1,
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

// //CHARGING POINTS


// const elecChargingPointApplication1: ElecChargePointsApplication = {
//     id: 1,
//     cpo: cpo,
//     station_count: 4,
//     charge_point_count: 90,
//     power_total: 8,
//     application_date: "2023-10-12",
//     status: ElecChargePointsApplicationStatus.Pending,
// }

// const elecChargingPointApplication2: ElecChargePointsApplication = {
//     id: 2,
//     cpo: cpo,
//     station_count: 19,
//     charge_point_count: 987,
//     power_total: 30000,
//     application_date: "2023-11-13",
//     validation_date: "2023-11-01",
//     status: ElecChargePointsApplicationStatus.Accepted,
// }
// const elecChargingPointApplication3: ElecChargePointsApplication = {
//     id: 3,
//     cpo: cpo,
//     station_count: 1,
//     charge_point_count: 5,
//     power_total: 1000,
//     application_date: "2023-09-01",
//     status: ElecChargePointsApplicationStatus.Rejected,
// }

// export const elecChargePointsApplications: ElecChargePointsApplication[] = [
//     elecChargingPointApplication1,
//     elecChargingPointApplication2,
//     elecChargingPointApplication3
// ]


// export const chargePointsApplicationError1: ChargePointsApplicationError = {
//     line: 12,
//     error: "MISSING_CHARGING_POINT_IN_DATAGOUV",
//     meta: "8U7Y"
// }
// export const chargePointsApplicationError2: ChargePointsApplicationError = {
//     line: 87,
//     error: "UNKNOW_ERROR"
// }
// export const elecChargePointsApplicationCheckResponseFailed: ElecChargePointsApplicationCheckInfo = {
//     file_name: "test.csv",
//     error_count: 2,
//     charge_point_count: 0,
//     errors: [chargePointsApplicationError1, chargePointsApplicationError2
//     ]
// }

// export const elecChargePointsApplicationCheckResponseSucceed: ElecChargePointsApplicationCheckInfo = {
//     file_name: "test.csv",
//     error_count: 0,
//     charge_point_count: 90
// }

// // METER READINGS

// const elecMeterReadingApplication1: ElecMeterReadingsApplication = {
//     id: 1,
//     cpo: cpo,
//     station_count: 4,
//     charge_point_count: 90,
//     energy_total: 8,
//     year: 2023,
//     quarter: 1,
//     application_date: "2023-11-13",

//     status: ElecMeterReadingsApplicationStatus.Accepted,
// }

// const elecMeterReadingApplication2: ElecMeterReadingsApplication = {
//     id: 1,
//     cpo: cpo,
//     station_count: 19,
//     charge_point_count: 1000,
//     energy_total: 30000,
//     year: 2023,
//     quarter: 2,
//     application_date: "2023-11-13",

//     status: ElecMeterReadingsApplicationStatus.Pending,
// }
// const elecMeterReadingApplication3: ElecMeterReadingsApplication = {
//     id: 1,
//     cpo: cpo,
//     station_count: 19,
//     charge_point_count: 1000,
//     energy_total: 30000,
//     year: 2023,
//     quarter: 2,
//     application_date: "2023-11-13",

//     status: ElecMeterReadingsApplicationStatus.Rejected,
// }


// export const elecMeterReadingsApplications: ElecMeterReadingsApplication[] = [
//     elecMeterReadingApplication1,
//     elecMeterReadingApplication2,
//     elecMeterReadingApplication3
// ]



// export const meterReadingsApplicationError1: MeterReadingsApplicationError = {
//     line: 87,
//     error: "UNKNOW_ERROR"
// }
// export const meterReadingsApplicationCheckResponseFailed: ElecMeterReadingsApplicationCheckInfo = {
//     file_name: "test.csv",
//     error_count: 1,
//     year: 2023,
//     quarter: 2,
//     charge_point_count: 2,
//     errors: [meterReadingsApplicationError1]
// }

// export const meterReadingsApplicationCheckResponseSuccess: ElecMeterReadingsApplicationCheckInfo = {
//     file_name: "test.csv",
//     error_count: 0,
//     charge_point_count: 90,
//     quarter: 2,
//     year: 2023,
//     // pending_application_already_exists: true
// }