import {
  okCountrySearch,
  okDeliverySitesSearch,
  okErrorsTranslations,
  okFieldsTranslations,
  okProductionSitesSearch,
  okTranslations,
} from "carbure/__test__/api"
import {
  okChargePointsAddSuccess,
  okChargePointsApplications,
  okChargePointsCheckValid,
  okMeterReadingsAddSuccess,
  okMeterReadingsApplications,
  okMeterReadingsCheckError,
  okMeterReadingsCheckValid,
} from "elec/__test__/api"

import { setupServer } from "msw/lib/node"
import defaultSettingsRequests from "./api"

const allRequests = [
  ...Object.values(defaultSettingsRequests),
  okCountrySearch,
  okDeliverySitesSearch,
  okErrorsTranslations,
  okFieldsTranslations,
  okProductionSitesSearch,
  okTranslations,
  okChargePointsAddSuccess,
  okChargePointsApplications,
  okChargePointsCheckValid,
  okMeterReadingsAddSuccess,
  okMeterReadingsApplications,
  okMeterReadingsCheckError,
  okMeterReadingsCheckValid,
]

export default setupServer(...allRequests)
