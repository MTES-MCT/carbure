import { lot, producer } from "common/__test__/data"
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

import { clone } from "common/__test__/helpers"
import * as data from "./data"
import { okSettings } from "settings/__test__/api"

let snapshot: any
let lots: any
let adminLots: any
let adminSnapshot: any
let details: any

export function setSnapshot(nextSnapshot: any) {
  snapshot = clone(nextSnapshot)
}

export function setLots(nextLots: any) {
  lots = clone(nextLots)
}

export function setAdminSnapshot(nextSnapshot: any) {
  adminSnapshot = clone(nextSnapshot)
}

export function setAdminLots(nextLots: any) {
  adminLots = clone(nextLots)
}

// init data
setSnapshot(data.snapshot)
setLots(data.lots)
setAdminSnapshot(data.adminSnapshot)
setAdminLots(data.lots)

export const okLotsSummary = rest.get(
  "/api/v3/lots/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: data.lotsSummary }))
  }
)

export const okAdminSummary = rest.get(
  "/api/v3/admin/lots/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: data.generalSummary }))
  }
)

export const okAuditorSummary = rest.get(
  "/api/v3/auditor/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: data.generalSummary }))
  }
)

export const okDuplicateLot = rest.post(
  "/api/v3/lots/duplicate",
  (req, res, ctx) => {
    snapshot.lots.draft++

    lots.lots = [lots.lots[0], lots.lots[0]]
    lots.total = 2
    lots.returned = 2

    return res(ctx.json({ status: "success" }))
  }
)

export const okSendLots = rest.post(
  "/api/v3/lots/validate",
  (req, res, ctx) => {
    snapshot.lots.draft--
    snapshot.lots.tofix--
    snapshot.lots.validated++
    snapshot.lots.in++

    lots.lots = []

    if (details) {
      details.transaction.lot.status = "Validated"

      if (details.transaction.delivery_status === "AC") {
        details.transaction.delivery_status = "AA"
      }
    }

    return res(ctx.json({ status: "success" }))
  }
)

export const okDeleteLots = rest.post(
  "/api/v3/lots/delete",
  (req, res, ctx) => {
    snapshot.lots.draft--
    snapshot.lots.tofix--
    lots.lots = []
    return res(ctx.json({ status: "success" }))
  }
)

export const okComment = rest.post("/api/v3/lots/comment", (req, res, ctx) => {
  details.comments.push({
    entity: producer,
    topic: "both",
    comment: (req.body as FormData).get("comment"),
  })

  return res(ctx.json({ status: "success" }))
})

export const okAcceptLot = rest.post("/api/v3/lots/accept", (req, res, ctx) => {
  snapshot.lots.in--
  snapshot.lots.accepted++

  lots.lots = []

  if (details) {
    details.transaction.lot.status = "Validated"
    details.transaction.delivery_status = "A"
  }

  return res(ctx.json({ status: "success" }))
})

export const okAcceptWithReserve = rest.post(
  "/api/v3/lots/accept-with-reserves",
  (req, res, ctx) => {
    lots.lots[0].lot.status = "Validated"
    lots.lots[0].delivery_status = "AC"

    if (details) {
      details.transaction.lot.status = "Validated"
      details.transaction.delivery_status = "AC"
    }

    return res(ctx.json({ status: "success" }))
  }
)

export const okRejectLot = rest.post("/api/v3/lots/reject", (req, res, ctx) => {
  snapshot.lots.in--
  lots.lots = []
  details = null
  return res(ctx.json({ status: "success" }))
})

export const okLotDetails = rest.get(
  "/api/v3/lots/details",
  (req, res, ctx) => {
    if (details === null) {
      return res(
        ctx.status(404),
        ctx.json({ status: "error", message: "not found" })
      )
    }

    return res(ctx.json({ status: "success", data: details }))
  }
)

export const okAdminLots = rest.get("/api/v3/admin/lots", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: adminLots }))
})

export const okAdminSnapshot = rest.get(
  "/api/v3/admin/lots/snapshot",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: adminSnapshot }))
  }
)

export const okFilters = rest.get("/api/v3/lots/filters", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.getFilter(req.url.searchParams.get("field") ?? ""),
    })
  )
})

export const okAdminFilters = rest.get(
  "/api/v3/admin/lots/filters",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: data.getFilter(req.url.searchParams.get("field") ?? ""),
      })
    )
  }
)

export const okAuditorFilters = rest.get(
  "/api/v3/auditor/filters",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: data.getFilter(req.url.searchParams.get("field") ?? ""),
      })
    )
  }
)

export const okSnapshot = rest.get("/api/snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        lots: {
          draft: 0,
          in_total: 0,
          in_pending: 0,
          in_tofix: 0,
          stock: 0,
          stock_total: 0,
          out_total: 0,
          out_pending: 0,
          out_tofix: 0,
        },
      },
    })
  )
})

export const okLots = rest.get("/api/lots", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        data: {
          lots: [],
          from: 0,
          returned: 0,
          total: 0,
          total_errors: 0,
          total_deadline: 0,
          errors: {},
        },
      },
    })
  )
})

export const okYears = rest.get("/api/years", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [],
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

export const okSummary = rest.get("/api/lots/summary", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        count: 2,
        total_volume: 24690,
        in: [
          {
            supplier: "ROQUETTE",
            biofuel_code: "ETH",
            volume_sum: 12345,
            avg_ghg_reduction: 76.15,
            total: 1,
            pending: 1,
          },
        ],
        out: [
          {
            client: "TERF",
            biofuel_code: "ETH",
            volume_sum: 12345,
            avg_ghg_reduction: 78.57,
            total: 1,
            pending: 0,
          },
        ],
      },
    })
  )
})

export default setupServer(
  okSettings,
  okSnapshot,
  okLots,
  okDuplicateLot,
  okSendLots,
  okDeleteLots,
  okComment,
  okAcceptLot,
  okAcceptWithReserve,
  okRejectLot,
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
  okLotDetails,
  okAdminLots,
  okAdminSnapshot,
  okLotsSummary,
  okAuditorSummary,
  okDeclarations,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
  okFilters,
  okAdminFilters,
  okAuditorFilters,
  okAdminSummary,
  okSummary
)
