import {
  okCountrySearch,
  okDeliverySitesSearch,
  okProductionSitesSearch,
} from "common/__test__/api"
import {
  okChargePointsAddSuccess,
  okChargePointsApplications,
  okChargePointsCheckValid,
  okMeterReadingsAddSuccess,
  okMeterReadingsApplications,
  okMeterReadingsCheckError,
  okMeterReadingsCheckValid,
} from "elec-charge-points/__test__/api"

import { setupServer } from "msw/node"
import defaultSettingsRequests from "./api"

const allRequests = [
  ...Object.values(defaultSettingsRequests),
  okCountrySearch,
  okDeliverySitesSearch,
  okProductionSitesSearch,
  okChargePointsAddSuccess,
  okChargePointsApplications,
  okChargePointsCheckValid,
  okMeterReadingsAddSuccess,
  okMeterReadingsApplications,
  okMeterReadingsCheckError,
  okMeterReadingsCheckValid,
]

export default setupServer(...allRequests)
