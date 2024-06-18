import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers";
import { elecChargePointApplicationDetailsInProgress, elecChargePointApplicationDetailsPending, elecAuditApplicationSample, elecMeterReadingApplicationDetailsInProgress, elecMeterReadingApplicationDetailsPending, elecMeterReadingApplicationAccepted, elecChargePointApplicationAccepted, elecChargePointApplicationRejected } from "elec/__test__/data";
import { elecAdminAuditSnapshot, elecAdminChargePointsApplicationsList, elecAdminMeterReadingsApplicationsList, elecAuditAdminMeterReadingsFilters } from "./data";

export const okGetSnapshot = mockGetWithResponseData("/elec/admin/audit/snapshot", elecAdminAuditSnapshot)
export const okGetYears = mockGetWithResponseData("/elec/admin/audit/years", [2023, 2024])

/***  Charge points ***/
export const okGetChargePointsApplications = mockGetWithResponseData("/elec/admin/audit/charge-points/applications", elecAdminChargePointsApplicationsList)
export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationDetailsPending)
// export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationDetailsInProgress)
// export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationAccepted)
// export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationRejected)
export const okGenerateSample = mockPostWithResponseData("/elec/admin/audit/charge-points/generate-sample", elecAuditApplicationSample)
export const okStartChargePointsApplicationAudit = mockPostWithResponseData("/elec/admin/audit/charge-points/start-audit")


/*** Meter readings ***/
export const okGetMeterReadingsApplications = mockGetWithResponseData("/elec/admin/audit/meter-readings/applications", elecAdminMeterReadingsApplicationsList)
export const okGetMeterReadingsApplicationsFilters = mockGetWithResponseData("/elec/admin/audit/meter-readings/filters", elecAuditAdminMeterReadingsFilters)
export const okGetMeterReadingsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/meter-readings/application-details", elecMeterReadingApplicationDetailsPending)
// export const okGetMeterReadingsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/meter-readings/application-details", elecMeterReadingApplicationDetailsInProgress)
// export const okGetMeterReadingsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/meter-readings/application-details", elecMeterReadingApplicationAccepted)
export const okMeterReadingsGenerateSample = mockPostWithResponseData("/elec/admin/audit/meter-readings/generate-sample", elecAuditApplicationSample)
export const okStartMeterReadingsApplicationAudit = mockPostWithResponseData("/elec/admin/audit/meter-readings/start-audit")
