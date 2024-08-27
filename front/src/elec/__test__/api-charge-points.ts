import { mockGetWithResponseData } from "carbure/__test__/helpers"
import {
  elecChargePointsYears,
  elecChargePointsSnapshot,
} from "./data-charge-points"

export const okChargePointsYears = mockGetWithResponseData(
  "/elec/charge-points/years",
  elecChargePointsYears
)

export const okChargePointsSnapshot = mockGetWithResponseData(
  "/elec/charge-points/snapshot",
  elecChargePointsSnapshot
)
