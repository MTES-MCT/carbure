import { rest } from "msw"
import { setupServer } from "msw/node"
import { okDynamicSettings } from "settings/__test__/api"
import {
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
} from "common/__test__/api"
import { lot } from "lot-details/__test__/data"

export const okAddLot = rest.post("/api/lots/add", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: lot,
    })
  )
})

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
