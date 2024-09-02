import { mockGetWithResponseData } from "carbure/__test__/helpers"
import { chargePointsList } from "./data"

export const okChargePointsList = mockGetWithResponseData(
  "/elec/charge-points/list",
  chargePointsList
)
