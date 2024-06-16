import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers";
import { elecChargePointApplicationDetailsInProgress, elecChargePointsApplicationSample, elecMeterReadingApplicationDetailsInProgress, elecMeterReadingApplicationDetailsPending } from "elec/__test__/data";
import { elecAdminAuditSnapshot, elecAdminChargePointsApplicationsList, elecAdminMeterReadingsApplicationsList } from "./data";

export const okGetSnapshot = mockGetWithResponseData("/elec/admin/audit/snapshot", elecAdminAuditSnapshot)

export const okGetChargePointsApplications = mockGetWithResponseData("/elec/admin/audit/charge-points/applications", elecAdminChargePointsApplicationsList)
// export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationDetailsPending)
export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationDetailsInProgress)
export const okGenerateSample = mockPostWithResponseData("/elec/admin/audit/charge-points/generate-sample", elecChargePointsApplicationSample)
export const okStartChargePointsApplicationAudit = mockPostWithResponseData("/elec/admin/audit/charge-points/start-audit")


export const okGetMeterReadingsApplications = mockGetWithResponseData("/elec/admin/audit/meter-readings/applications", elecAdminMeterReadingsApplicationsList)
export const okGetMeterReadingsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/meter-readings/application-details", elecMeterReadingApplicationDetailsPending)
// export const okGetMeterReadingsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/meter-readings/application-details", elecMeterReadingApplicationDetailsInProgress)
export const okMeterReadingsGenerateSample = mockPostWithResponseData("/elec/admin/audit/meter-readings/generate-sample", elecChargePointsApplicationSample)
export const okStartMeterReadingsApplicationAudit = mockPostWithResponseData("/elec/admin/audit/meter-readings/start-audit")
