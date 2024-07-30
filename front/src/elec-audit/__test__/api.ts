import { mockGetWithResponseData } from "carbure/__test__/helpers"
import { elecChargePointApplicationDetailsInProgress } from "elec/__test__/data"
import {
  elecAuditCPOFilters,
  elecAuditChargePointsApplicationsList,
  elecAuditSnapshot,
  elecAuditYears,
} from "./data"

export const okGetYears = mockGetWithResponseData(
  "/elec/audit/years",
  elecAuditYears
)
export const okGetSnapshot = mockGetWithResponseData(
  "/elec/audit/snapshot",
  elecAuditSnapshot
)
export const okGetApplicationsFilters = mockGetWithResponseData(
  "/elec/audit/filters",
  elecAuditCPOFilters
)

export const okGetChargePointsApplications = mockGetWithResponseData(
  "/elec/audit/applications",
  elecAuditChargePointsApplicationsList
)

export const okGetChargePointsApplicationDetails = mockGetWithResponseData(
  "/elec/audit/application-details",
  elecChargePointApplicationDetailsInProgress
)
