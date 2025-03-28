import {
  mockGetWithResponseData,
  mockPostWithResponseData,
} from "common/__test__/helpers"
import {
  elecChargePointsApplicationCheckResponseFailed,
  elecChargePointsApplicationCheckResponseSucceed,
  elecChargePointsApplications,
  elecMeterReadingsApplicationsResponseMissing,
  elecMeterReadingsApplicationsResponsePending,
  elecMeterReadingsApplicationsWithoutChargePointsResponse,
  elecSnapshot,
  meterReadingsApplicationCheckResponseFailed,
  meterReadingsApplicationCheckResponseSuccess,
} from "elec/__test__/data"
import { http, HttpResponse } from "msw"

export const okChargePointsApplications = http.get(
  "/api/elec/cpo/charge-points/applications",
  ({ request }) => {
    let data = elecChargePointsApplications
    const searchParams = new URLSearchParams(request.url)
    const year = searchParams.get("year")

    if (year) {
      data = data.filter((chargePointApplication) =>
        chargePointApplication.application_date.includes(year)
      )
    }

    return HttpResponse.json({
      status: "success",
      data,
    })
  }
)

export const okCPOSnapshot = mockGetWithResponseData(
  "/elec/cpo/certificate-snapshot",
  elecSnapshot
)

export const okChargePointsApplicationsEmpty = mockGetWithResponseData(
  "/elec/cpo/charge-points/applications",
  []
)
export const okChargePointsCheckValid = mockPostWithResponseData(
  "/elec/cpo/charge-points/check-application",
  elecChargePointsApplicationCheckResponseSucceed
)
export const okChargePointsCheckError = mockPostWithResponseData(
  "/elec/cpo/charge-points/check-application",
  elecChargePointsApplicationCheckResponseFailed,
  true
)
export const okChargePointsAddSuccess = mockPostWithResponseData(
  "/elec/cpo/charge-points/add-application"
)

export const okMeterReadingsApplicationsEmpty = mockGetWithResponseData(
  "/elec/cpo/meter-readings/applications",
  []
)
export const okMeterReadingsApplications = mockGetWithResponseData(
  "/elec/cpo/meter-readings/applications",
  elecMeterReadingsApplicationsResponsePending
)
export const okMeterReadingsApplicationsWithoutChargePoints =
  mockGetWithResponseData(
    "/elec/cpo/meter-readings/applications",
    elecMeterReadingsApplicationsWithoutChargePointsResponse
  )
export const okMeterReadingsApplicationsUrgencyCritical =
  mockGetWithResponseData(
    "/elec/cpo/meter-readings/applications",
    elecMeterReadingsApplicationsResponseMissing
  )
export const okMeterReadingsCheckError = mockPostWithResponseData(
  "/elec/cpo/meter-readings/check-application",
  meterReadingsApplicationCheckResponseFailed,
  true,
  "VALIDATION_FAILED"
)
export const okMeterReadingsCheckValid = mockPostWithResponseData(
  "/elec/cpo/meter-readings/check-application",
  meterReadingsApplicationCheckResponseSuccess
)
export const okMeterReadingsAddSuccess = mockPostWithResponseData(
  "/elec/cpo/meter-readings/add-application"
)
