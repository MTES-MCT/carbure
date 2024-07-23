import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers"
import { elecChargePointApplicationDetailsInProgress } from "elec/__test__/data"
import {
  elecAuditApplicationCheckReportError,
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


export const okCheckAuditReportError = mockPostWithResponseData("/elec/auditor/check-report", elecAuditApplicationCheckReportError)
export const okCheckAuditReportSuccess = mockPostWithResponseData("/elec/auditor/check-report", elecAuditApplicationCheckReportSuccess)