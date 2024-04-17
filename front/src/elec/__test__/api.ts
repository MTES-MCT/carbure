import { rest } from "msw"
import { setupServer } from "msw/node"


import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers"
import { elecChargePointsApplicationCheckResponseFailed, elecChargePointsApplicationCheckResponseSucceed, elecChargePointsApplications, elecMeterReadingsApplications, elecMeterReadingsApplicationsResponseMissing, elecMeterReadingsApplicationsResponsePending, meterReadingsApplicationCheckResponseFailed, meterReadingsApplicationCheckResponseSuccess } from "elec/__test__/data"



export const okChargePointsApplications = rest.get("/api/elec/cpo/charge-points/applications", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: elecChargePointsApplications,
    })
  )
})

export const okChargePointsApplicationsEmpty = mockGetWithResponseData("/api/elec/cpo/charge-points/applications", [])
export const okChargePointsCheckValid = mockPostWithResponseData("/api/elec/cpo/charge-points/check-application", elecChargePointsApplicationCheckResponseSucceed)
export const okChargePointsCheckError = mockPostWithResponseData("/api/elec/cpo/charge-points/check-application", elecChargePointsApplicationCheckResponseFailed, true)
export const okChargePointsAddSuccess = mockPostWithResponseData("/api/elec/cpo/charge-points/add-application")

export const okMeterReadingsApplicationsEmpty = mockGetWithResponseData("/api/elec/cpo/meter-readings/applications", [])
export const okMeterReadingsApplications = mockGetWithResponseData("/api/elec/cpo/meter-readings/applications", elecMeterReadingsApplicationsResponsePending)
export const okMeterReadingsApplicationsUrgencyCritical = mockGetWithResponseData("/api/elec/cpo/meter-readings/applications", elecMeterReadingsApplicationsResponseMissing)
export const okMeterReadingsCheckError = mockPostWithResponseData("/api/elec/cpo/meter-readings/check-application", meterReadingsApplicationCheckResponseFailed, true, "VALIDATION_FAILED")
export const okMeterReadingsCheckValid = mockPostWithResponseData("/api/elec/cpo/meter-readings/check-application", meterReadingsApplicationCheckResponseSuccess)
export const okMeterReadingsAddSuccess = mockPostWithResponseData("/api/elec/cpo/meter-readings/add-application")

