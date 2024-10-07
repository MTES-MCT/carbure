import { admin, entityRight } from "carbure/__test__/data"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"

import {
  okTranslations,
  okFieldsTranslations,
  okErrorsTranslations,
} from "carbure/__test__/api"

import { getFilter } from "transactions/__test__/data"
import { lotSummary, lots } from "./data"

export const okAdminSettings = http.get("/api/user", () => {
  return HttpResponse.json({
    status: "success",
    data: {
      email: "admin@test.com",
      rights: [{ ...entityRight, entity: admin }],
      requests: [{ ...entityRight, entity: admin }],
    },
  })
})

export const okLotsSummary = http.get(
  "/api/transactions/admin/lots/summary",
  () => {
    return HttpResponse.json({ status: "success", data: lotSummary })
  }
)

export const okFilters = http.get(
  "/api/transactions/admin/lots/filters",
  ({ request }) => {
    const searchParams = new URLSearchParams(request.url)
    return HttpResponse.json({
      status: "success",
      data: getFilter(searchParams.get("field") ?? ""),
    })
  }
)

export const okSnapshot = http.get("/api/transactions/admin/snapshot", () => {
  return HttpResponse.json({
    status: "success",
    data: {
      lots: {
        alerts: 0,
        lots: 0,
        stocks: 0,
      },
    },
  })
})

export const okLots = http.get("/api/transactions/admin/lots", () => {
  return HttpResponse.json({
    status: "success",
    data: {
      lots: lots,
      from: 0,
      returned: 3,
      total: 3,
      total_errors: 0,
      total_deadline: 0,
      errors: {},
    },
  })
})

export const okStocks = http.get("/api/transactions/admin/stocks", () => {
  return HttpResponse.json({
    status: "success",
  })
})

export const okYears = http.get("/api/transactions/admin/years", () => {
  return HttpResponse.json({
    status: "success",
    data: [],
  })
})

export default setupServer(
  okSnapshot,
  okLots,
  okLotsSummary,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
  okFilters,
  okYears,
  okSnapshot,
  okStocks,
  okAdminSettings
)
