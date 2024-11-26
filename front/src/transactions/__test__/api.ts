import { producer } from "carbure/__test__/data"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"

import { Data } from "carbure/__test__/helpers"
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
} from "carbure/__test__/api"

import * as data from "./data"
import {
  okDeliverySites,
  okDynamicSettings,
  okSettings,
} from "settings/__test__/api"
import { Snapshot, LotList } from "transactions/types"

// init data
Data.set("snapshot", data.emptySnapshot)
Data.set("lots", data.lots)

export const okSnapshot = http.get("/api/transactions/snapshot", () => {
  return HttpResponse.json({
    status: "success",
    data: Data.get("snapshot"),
  })
})

export const okLots = http.get("/api/transactions/lots", () => {
  return HttpResponse.json({
    status: "success",
    data: Data.get("lots"),
  })
})

export const okYears = http.get("/api/transactions/years", () => {
  return HttpResponse.json({
    status: "success",
    data: [2021],
  })
})

export const okDeclarations = http.get("/api/transactions/declarations", () => {
  return HttpResponse.json({
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
})

export const okFilters = http.get(
  "/api/transactions/lots/filters",
  ({ request }) => {
    const searchParams = new URLSearchParams(request.url)
    return HttpResponse.json({
      status: "success",
      data: data.getFilter(searchParams.get("field") ?? ""),
    })
  }
)

export const okSummary = http.get("/api/transactions/lots/summary", () => {
  return HttpResponse.json({
    status: "success",
    data: data.lotSummary,
  })
})

export const okSendLot = http.post("/api/transactions/lots/send", () => {
  Data.set("lots", (lots: LotList) => {
    lots.lots = []
    lots.ids = []
    lots.returned = 0
    lots.total = 0
  })
  Data.set("snapshot", (snapshot: Snapshot) => {
    snapshot.draft -= 1
    snapshot.out_total += 1
  })
  return HttpResponse.json({ status: "success" })
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

  okDynamicSettings,
  okDeliverySites,

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
