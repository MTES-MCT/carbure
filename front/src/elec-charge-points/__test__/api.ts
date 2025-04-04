import { mockGetWithResponseData } from "common/__test__/helpers"
import { elecChargePointsYears, elecChargePointsSnapshot } from "./data"

export const okChargePointsYears = mockGetWithResponseData(
  "/elec/charge-points/years",
  elecChargePointsYears
)

export const okChargePointsSnapshot = mockGetWithResponseData(
  "/elec/charge-points/snapshot",
  elecChargePointsSnapshot
)
