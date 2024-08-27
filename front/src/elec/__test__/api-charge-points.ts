import { mockGetWithResponseData } from "carbure/__test__/helpers"
import { rest } from "msw"
import { elecChargePointsApplications } from "./data"
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

export const okChargePointsApplication = rest.get(
  "/api/elec/charge-points/applications",
  (req, res, ctx) => {
    let data = elecChargePointsApplications
    const year = req.url.searchParams.get("year")

    if (year) {
      data = data.filter((chargePointApplication) =>
        chargePointApplication.application_date.includes(year)
      )
    }

    return res(
      ctx.json({
        status: "success",
        data,
      })
    )
  }
)
