import { producer } from "common/__test__/data"
import { rest } from "msw"
import { setupServer } from "msw/node"

import {
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
  okTranslations,
  okFieldsTranslations,
  okErrorsTranslations,
} from "common/__test__/api"

import { Data } from "common/__test__/helpers"
import * as data from "./data"
import { okSettings } from "settings/__test__/api"
import { Snapshot, LotList } from "transactions/types"

// init data
Data.set("snapshot", data.emptySnapshot)
Data.set("lots", data.lots)

export const okSnapshot = rest.get("/api/snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: Data.get("snapshot"),
    })
  )
})

export const okLots = rest.get("/api/lots", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: Data.get("lots"),
    })
  )
})

export const okYears = rest.get("/api/years", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [2021],
    })
  )
})
export const okDeclarations = rest.get("/api/declarations", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [
        {
          period: 202101,
          lots: 2,
          pending: 1,
          declaration: {
            id: 1638,
            entity: producer,
            declared: false,
            period: "2021-01-01",
            deadline: "2021-02-28",
            checked: false,
            month: 1,
            year: 2021,
            reminder_count: 0,
          },
        },
      ],
    })
  )
})

export const okFilters = rest.get("/api/lots/filters", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.getFilter(req.url.searchParams.get("field") ?? ""),
    })
  )
})

export const okSummary = rest.get("/api/lots/summary", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.lotSummary,
    })
  )
})

export const okSendLot = rest.post("/api/lots/send", (req, res, ctx) => {
  Data.set("lots", (lots: LotList) => {
    lots.lots = []
    lots.ids = []
    lots.returned = 0
    lots.total = 0
  })
  Data.set("snapshot", (snapshot: Snapshot) => {
    snapshot.lots.draft -= 1
    snapshot.lots.out_total += 1
  })
  return res(ctx.json({ status: "success" }))
})

export default setupServer(
  okSettings,
  okSnapshot,
  okLots,
  okFilters,
  okSummary,
  okDeclarations,
  okYears,

  okSendLot,

  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,

  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations
)
