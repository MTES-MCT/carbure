import { rest } from "msw"
import { setupServer } from "msw/node"

import * as data from "./data"

let snapshot: any
let lots: any

export function setSnapshot(nextSnapshot: any) {
  snapshot = JSON.parse(JSON.stringify(nextSnapshot))
}

export function setLots(nextLots: any) {
  lots = JSON.parse(JSON.stringify(nextLots))
}

// init data
setSnapshot(data.snapshot)
setSnapshot(data.lots)

export const okSnapshot = rest.get("/api/v3/lots/snapshot", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: snapshot }))
})

export const okLots = rest.get("/api/v3/lots", (req, res, ctx) => {
  return res(ctx.json({ status: "success", data: lots }))
})

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
    return res(ctx.json({ status: "success" }))
  }
)

export const okSendAll = rest.post(
  "/api/v3/lots/validate-all-drafts",
  (req, res, ctx) => {
    snapshot.lots.draft--
    snapshot.lots.validated++
    snapshot.lots.in++
    lots.lots = []
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

export const okDeleteAll = rest.post(
  "/api/v3/lots/delete-all-drafts",
  (req, res, ctx) => {
    snapshot.lots.draft--
    lots.lots = []
    return res(ctx.json({ status: "success" }))
  }
)

export const okComment = rest.post("/api/v3/lots/comment", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okAcceptLot = rest.post("/api/v3/lots/accept", (req, res, ctx) => {
  snapshot.lots.in--
  snapshot.lots.accepted++
  lots.lots = []
  return res(ctx.json({ status: "success" }))
})

export const okAcceptWithReserve = rest.post(
  "/api/v3/lots/accept-with-reserves",
  (req, res, ctx) => {
    lots.lots[0].lot.status = "Validated"
    lots.lots[0].delivery_status = "AC"
    return res(ctx.json({ status: "success" }))
  }
)

export const okAcceptAll = rest.post(
  "/api/v3/lots/accept-all",
  (req, res, ctx) => {
    snapshot.lots.in--
    snapshot.lots.accepted++
    lots.lots = []
    return res(ctx.json({ status: "success" }))
  }
)

export const okRejectLot = rest.post("/api/v3/lots/reject", (req, res, ctx) => {
  snapshot.lots.in--
  lots.lots = []
  return res(ctx.json({ status: "success" }))
})

export const okRejectAll = rest.post(
  "/api/v3/lots/reject-all",
  (req, res, ctx) => {
    snapshot.lots.in--
    lots.lots = []
    return res(ctx.json({ status: "success" }))
  }
)

export default setupServer(
  okSnapshot,
  okLots,
  okDuplicateLot,
  okSendLots,
  okSendAll,
  okDeleteLots,
  okDeleteAll,
  okComment,
  okAcceptLot,
  okAcceptWithReserve,
  okAcceptAll,
  okRejectLot,
  okRejectAll
)
