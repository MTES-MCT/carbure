import { EntityType } from "common/types"
import {
  okErrorsTranslations,
  okFieldsTranslations,
  okTranslations,
} from "common/__test__/api"
import { rest } from "msw"
import { setupServer } from "msw/node"
import { okSettings } from "settings/__test__/api"
import { okLotsSummary } from "transactions/__test__/api-old"
import { okLots, okSnapshot, okYears } from "transactions/__test__/api"

export const okStats = rest.get("/api/v3/common/stats", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        total_volume: 1000000,
        entities: {
          [EntityType.Operator]: 25,
          [EntityType.Producer]: 25,
          [EntityType.Trader]: 25,
        },
      },
    })
  )
})

export default setupServer(
  okSettings,
  okSnapshot,
  okYears,
  okLots,
  okLotsSummary,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
  okStats
)
