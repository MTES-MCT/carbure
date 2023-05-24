import { admin, entityRight } from "carbure/__test__/data"
import { rest } from "msw"
import { setupServer } from "msw/node"

import {
  okTranslations,
  okFieldsTranslations,
  okErrorsTranslations,
} from "carbure/__test__/api"

import { getFilter } from "transactions/__test__/data"
import { lotSummary } from "./data"
import { lots } from "./data"

export const okAdminSettings = rest.get("/api/v5/user", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "admin@test.com",
        rights: [{ ...entityRight, entity: admin }],
        requests: [{ ...entityRight, entity: admin }],
      },
    })
  )
})

export const okLotsSummary = rest.get(
  "/api/v5/admin/controls/lots/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: lotSummary }))
  }
)

export const okFilters = rest.get(
  "/api/v5/admin/controls/lots/filters",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: getFilter(req.url.searchParams.get("field") ?? ""),
      })
    )
  }
)

export const okSnapshot = rest.get("/api/v5/admin/controls/snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        lots: {
          alerts: 0,
          lots: 0,
          stocks: 0,
        },
      },
    })
  )
})

export const okLots = rest.get("/api/v5/admin/controls/lots", (req, res, ctx) => {
  return res(
    ctx.json({
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
  )
})

export const okStocks = rest.get("/api/v5/admin/controls/stocks", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
    })
  )
})

export const okYears = rest.get("/api/v5/admin/controls/years", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [],
    })
  )
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
