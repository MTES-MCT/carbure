import { mockGetWithResponseData } from "carbure/__test__/helpers"
import { elecChargePointApplicationDetailsInProgress } from "elec/__test__/data"
import {
  elecAuditCPOFilters,
  elecAuditChargePointsApplicationsList,
  elecAuditSnapshot,
  elecAuditYears,
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

export const okGetChargePointsApplications = mockGetWithResponseData(
  "/elec/auditor/applications",
  elecAuditChargePointsApplicationsList
)

export const okGetChargePointsApplicationDetails = mockGetWithResponseData(
  "/elec/auditor/application-details",
  elecChargePointApplicationDetailsInProgress
)
