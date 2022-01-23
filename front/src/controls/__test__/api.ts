import { admin, entityRight } from "common/__test__/data"
import { rest } from "msw"
import { setupServer } from "msw/node"

import {
  okTranslations,
  okFieldsTranslations,
  okErrorsTranslations,
} from "common/__test__/api"

import { getFilter } from "transactions/__test__/data"
import { lotSummary } from "./data"

export const okAdminSettings = rest.get("/api/v3/settings", (req, res, ctx) => {
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
  "/api/admin/lots/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: lotSummary }))
  }
)

export const okFilters = rest.get(
  "/api/admin/lots/filters",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: getFilter(req.url.searchParams.get("field") ?? ""),
      })
    )
  }
)

export const okSnapshot = rest.get("/api/admin/snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        lots: {
          alerts: 0,
          corrections: 0,
          declarations: 0,
          pinned: 0,
        },
      },
    })
  )
})

export const okLots = rest.get("/api/admin/lots", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        lots: [],
        from: 0,
        returned: 0,
        total: 0,
        total_errors: 0,
        total_deadline: 0,
        errors: {},
      },
    })
  )
})

export const okYears = rest.get("/api/admin/years", (req, res, ctx) => {
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
  okAdminSettings
)
