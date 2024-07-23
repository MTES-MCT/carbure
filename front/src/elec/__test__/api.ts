import {
	mockGetWithResponseData,
	mockPostWithResponseData,
} from "carbure/__test__/helpers"
import {
	elecChargePointsApplicationCheckResponseFailed,
	elecChargePointsApplicationCheckResponseSucceed,
	elecChargePointsApplications,
	elecMeterReadingsApplicationsResponseMissing,
	elecMeterReadingsApplicationsResponsePending,
	elecSnapshot,
	meterReadingsApplicationCheckResponseFailed,
	meterReadingsApplicationCheckResponseSuccess,
} from "elec/__test__/data"

export const okChargePointsApplications = mockGetWithResponseData(
	"/elec/cpo/charge-points/applications",
	elecChargePointsApplications
)
export const okCPOSnapshot = mockGetWithResponseData(
	"/elec/cpo/snapshot",
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
