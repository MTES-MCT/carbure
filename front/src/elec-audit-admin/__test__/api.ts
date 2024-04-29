import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers";
import { elecChargePointApplicationPending } from "elec/__test__/data";
import { elecAdminAuditSnapshot, elecAdminChargePointsApplicationsList, elecChargePointsApplicationSample } from "./data";

export const okGetSnapshot = mockGetWithResponseData("/elec/admin/audit/snapshot", elecAdminAuditSnapshot)
export const okGetChargePointsApplications = mockGetWithResponseData("/elec/admin/audit/charge-points/applications", elecAdminChargePointsApplicationsList)

export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationPending)
export const okGenerateSample = mockPostWithResponseData("/elec/admin/audit/charge-points/generate-sample", elecChargePointsApplicationSample)
export const okStartChargePointsApplicationAudit = mockPostWithResponseData("/elec/admin/audit/charge-points/start-audit")


