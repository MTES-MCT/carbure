import { http } from "msw"
import { setupServer } from "msw/node"
import { okDynamicSettings } from "settings/__test__/api"
import {
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
} from "carbure/__test__/api"
import { lot } from "transaction-details/__test__/data"

export const okAddLot = http.post(
  "/api/transactions/lots/add",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: lot,
      })
    )
  }
)

export default setupServer(
  okAddLot,

  okDynamicSettings,
  okBiocarburantsSearch,
  okMatierePremiereSearch,
  okEntitySearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okProductionSitesSearch
)
