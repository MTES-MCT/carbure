import { mockGetWithResponseData } from "carbure/__test__/helpers"
import { elecChargePointsYears } from "./data-charge-points"

export const okChargePointYears = mockGetWithResponseData(
  "/elec/charge-points/years",
  elecChargePointsYears
)
