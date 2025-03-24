import {
  mockGetWithResponseData,
  mockPostWithResponseData,
} from "common/__test__/helpers"
import {
  elecAuditApplicationCheckReportSuccess,
  elecAuditCPOFilters,
  elecAuditApplicationsList,
  elecAuditSnapshot,
  elecAuditYears,
  elecAuditorApplicationDetailsInProgress,
} from "./data"

export const okGetYears = mockGetWithResponseData(
  "/elec/auditor/years",
  elecAuditYears
)
export const okGetSnapshot = mockGetWithResponseData(
  "/elec/auditor/snapshot",
  elecAuditSnapshot
)
export const okGetApplicationsFilters = mockGetWithResponseData(
  "/elec/auditor/filters",
  elecAuditCPOFilters
)

export const okGetAuditApplications = mockGetWithResponseData(
  "/elec/auditor/applications",
  elecAuditApplicationsList
)

export const okGetChargePointsApplicationDetails = mockGetWithResponseData(
  "/elec/auditor/application-details",
  elecAuditorApplicationDetailsInProgress
)

// export const okCheckAuditReportError = mockPostWithResponseData("/elec/auditor/check-report", elecAuditApplicationCheckReportError)
export const okCheckAuditReportSuccess = mockPostWithResponseData(
  "/elec/auditor/check-report",
  elecAuditApplicationCheckReportSuccess
)

export const okAcceptAuditReport = mockPostWithResponseData(
  "/elec/auditor/accept-report",
  elecAuditApplicationCheckReportSuccess
)
