import { rest } from "msw"
import { setupServer } from "msw/node"


import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers"
import { elecChargingPointsApplicationCheckResponseFailed, elecChargingPointsApplicationCheckResponseSucceed, elecChargingPointsApplications } from "elec/__test__/data"



export const okChargingPointsApplications = rest.get("/api/elec/cpo/charging-points/applications", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: elecChargingPointsApplications,
    })
  )
})

export const okChargingPointsApplicationsEmpty = mockGetWithResponseData("/api/elec/cpo/charging-points/applications", [])
export const okChargingPointsCheckValid = mockPostWithResponseData("/api/elec/cpo/charging-points/check-application", elecChargingPointsApplicationCheckResponseSucceed)
export const okChargingPointsCheckError = mockPostWithResponseData("/api/elec/cpo/charging-points/check-application", elecChargingPointsApplicationCheckResponseFailed, true)
export const okChargingPointsAddSuccess = mockPostWithResponseData("/api/elec/cpo/charging-points/add-application")


