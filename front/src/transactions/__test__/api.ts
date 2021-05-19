import { lot, producer } from "common/__test__/data"
import { rest } from "msw"
import { setupServer } from "msw/node"

import {
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okErrors,
  okMatierePremiereSearch,
  okProductionSitesSearch,
  okTranslations,
} from "common/__test__/api"

import { clone } from "common/__test__/helpers"
import * as data from "./data"

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

export const okSnapshot = rest.get("/api/v3/lots/snapshot", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: snapshot }))
})

export const okLots = rest.get("/api/v3/lots", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: lots }))
})

export const okLotsSummary = rest.get(
  "/api/v3/lots/summary",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: data.lotsSummary }))
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

export const okAddLot = rest.post("/api/v3/lots/add", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: lot }))
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

export const okLotUpdate = rest.post("/api/v3/lots/update", (req, res, ctx) => {
  setDetails(data.lotDetails)
  details.transaction.dae = "DAETESTUPDATE Confirmer"
  return res(ctx.json({ status: "success" }))
})

export const okAdminLots = rest.get("/api/v3/admin/lots", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: adminLots }))
})

export const okAdminSnapshot = rest.get(
  "/api/v3/admin/lots/snapshot",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: adminSnapshot }))
  }
)

export default setupServer(
  okSnapshot,
  okLots,
  okDuplicateLot,
  okSendLots,
  okDeleteLots,
  okComment,
  okAcceptLot,
  okAcceptWithReserve,
  okRejectLot,
  okAddLot,
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
  okLotDetails,
  okLotUpdate,
  okAdminLots,
  okAdminSnapshot,
  okLotsSummary,
  okTranslations,
  okErrors
)
