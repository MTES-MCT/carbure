import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers";
import { elecChargePointApplicationAuditInProgress, elecChargePointApplicationDetailsInProgress, elecChargePointApplicationDetailsPending, elecChargePointApplicationPending, elecChargePointsApplicationSample } from "elec/__test__/data";
import { elecAdminAuditSnapshot, elecAdminChargePointsApplicationsList } from "./data";

export const okGetSnapshot = mockGetWithResponseData("/elec/admin/audit/snapshot", elecAdminAuditSnapshot)
export const okGetChargePointsApplications = mockGetWithResponseData("/elec/admin/audit/charge-points/applications", elecAdminChargePointsApplicationsList)

// export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationDetailsPending)
export const okGetChargePointsApplicationDetails = mockGetWithResponseData("/elec/admin/audit/charge-points/application-details", elecChargePointApplicationDetailsInProgress)
export const okGenerateSample = mockPostWithResponseData("/elec/admin/audit/charge-points/generate-sample", elecChargePointsApplicationSample)
export const okStartChargePointsApplicationAudit = mockPostWithResponseData("/elec/admin/audit/charge-points/start-audit")


