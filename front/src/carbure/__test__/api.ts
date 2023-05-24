import { rest } from "msw"
import { setupServer } from "msw/node"
import translations from "../../../public/locales/fr/translation.json"
import errors from "../../../public/locales/fr/errors.json"
import fields from "../../../public/locales/fr/fields.json"
import { EntityType } from "carbure/types"

import {
  country,
  deliverySite,
  producer,
  trader,
  operator,
  matierePremiere,
  biocarburant,
  productionSite,
} from "./data"

export const okStats = rest.get("/api/v5/home-stats", (req, res, ctx) => {
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

export const okNotifications = rest.get(
  "/api/v5/entity/notifications",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [],
      })
    )
  }
)

export const okEntitySearch = rest.get(
  "/api/v5/resources/entities",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [producer, trader, operator],
      })
    )
  }
)

export const okCountrySearch = rest.get(
  "/api/v5/resources/countries",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [country],
      })
    )
  }
)

export const okBiocarburantsSearch = rest.get(
  "/api/v5/resources/biofuels",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [biocarburant],
      })
    )
  }
)

export const okMatierePremiereSearch = rest.get(
  "/api/v5/resources/feedstocks",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [matierePremiere],
      })
    )
  }
)

export const okProductionSitesSearch = rest.get(
  "/api/v5/resources/production-sites",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [productionSite],
      })
    )
  }
)

export const okDeliverySitesSearch = rest.get(
  "/api/v5/resources/depots",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [deliverySite],
      })
    )
  }
)

export const okTranslations = rest.get(
  "/app/locales/fr/translations.json",
  (req, res, ctx) => {
    return res(ctx.json(translations))
  }
)

export const okErrorsTranslations = rest.get(
  "/app/locales/fr/errors.json",
  (req, res, ctx) => {
    return res(ctx.json(errors))
  }
)

export const okFieldsTranslations = rest.get(
  "/app/locales/fr/fields.json",
  (req, res, ctx) => {
    return res(ctx.json(fields))
  }
)

export default setupServer(
  okNotifications,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
  okStats
)
