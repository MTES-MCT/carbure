import { okErrorsTranslations, okFieldsTranslations, okTranslations } from "common/__test__/api"
import { setupServer } from "msw/node"
import { okSettings } from "settings/__test__/api"
import { okLots, okLotsSummary, okSnapshot } from "transactions/__test__/api"

export default setupServer(
  okSettings,
  okSnapshot,
  okLots,
  okLotsSummary,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
)
