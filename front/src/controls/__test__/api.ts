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

import { clone } from "common/__test__/helpers"
import * as data from "transactions/__test__/data"

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

export function setDetails(nextDetails: any) {
  details = clone(nextDetails)
}

// init data
setSnapshot(data.snapshot)
setLots(data.lots)
setDetails(data.lotDetails)
setAdminSnapshot(data.adminSnapshot)
setAdminLots(data.lots)

export const okLotsSummary = rest.get(
  "/api/admin/lots/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: data.lotsSummary }))
  }
)

export const okComment = rest.post(
  "/api/admin/lots/comment",
  (req, res, ctx) => {
    details.comments.push({
      entity: producer,
      topic: "both",
      comment: (req.body as FormData).get("comment"),
    })

    return res(ctx.json({ status: "success" }))
  }
)

export const okLotDetails = rest.get(
  "/api/admin/lots/details",
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

export const okFilters = rest.get(
  "/api/admin/lots/filters",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: data.getFilter(req.url.searchParams.get("field") ?? ""),
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

export const okLots = rest.get("/api/admin/lots", (req, res, ctx) => {
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
  okComment,
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
  okLotDetails,
  okLotsSummary,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
  okFilters
)
