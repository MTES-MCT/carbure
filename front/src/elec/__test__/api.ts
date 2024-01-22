import { rest } from "msw"
import { setupServer } from "msw/node"


import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers"
import { elecChargingPointsApplicationCheckResponseFailed, elecChargingPointsApplicationCheckResponseSucceed, elecChargingPointsApplications, elecMeterReadingsApplications, meterReadingsApplicationCheckResponseFailed, meterReadingsApplicationCheckResponseSuccess } from "elec/__test__/data"



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

export const okMeterReadingsApplicationsEmpty = mockGetWithResponseData("/api/elec/cpo/meter-readings/applications", [])
export const okMeterReadingsApplications = mockGetWithResponseData("/api/elec/cpo/meter-readings/applications", elecMeterReadingsApplications)
export const okMeterReadingsCheckError = mockPostWithResponseData("/api/elec/cpo/meter-readings/check-application", meterReadingsApplicationCheckResponseFailed, true, "VALIDATION_ERROR")
export const okMeterReadingsCheckValid = mockPostWithResponseData("/api/elec/cpo/meter-readings/check-application", meterReadingsApplicationCheckResponseSuccess)
export const okMeterReadingsAddSuccess = mockPostWithResponseData("/api/elec/cpo/meter-readings/add-application")

