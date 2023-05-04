import { rest } from "msw"
import { setupServer } from "msw/node"
import { Data } from "carbure/__test__/helpers"
import { LotDetails } from "../types"
import { CorrectionStatus, DeliveryType, LotStatus } from "transactions/types"
import { okDeliverySites, okDynamicSettings } from "settings/__test__/api"
import {
  okBiocarburantsSearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okEntitySearch,
  okMatierePremiereSearch,
  okProductionSitesSearch,
} from "carbure/__test__/api"
import { producer } from "carbure/__test__/data"

export const okLotDetails = rest.get("/api/lots/details", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: Data.get("lot-details"),
    })
  )
})

export const okUpdateLot = rest.post(
  "/api/v5/transactions/lots/update",
  (req, res, ctx) => {
    const details = Data.get("lot-details")
    details.lot.transport_document_reference = "DAETEST UPDATED"
    Data.set("lot-details", details)
    return res(ctx.json({ status: "success" }))
  }
)

export const okSendLot = rest.post("/api/lots/send", (req, res, ctx) => {
  Data.set("lot-details", (details: LotDetails) => {
    details.lot.lot_status = LotStatus.Pending
  })
  return res(ctx.json({ status: "success" }))
})

export const okDeleteLot = rest.post("/api/lots/delete", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okRequestFix = rest.post(
  "/api/v5/transactions/lots/request-fix",
  (req, res, ctx) => {
    Data.set("lot-details", (details: LotDetails) => {
      details.lot.correction_status = CorrectionStatus.InCorrection
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okMarkAsFixed = rest.post(
  "/api/v5/transactions/lots/submit-fix",
  (req, res, ctx) => {
    Data.set("lot-details", (details: LotDetails) => {
      details.lot.correction_status = CorrectionStatus.Fixed
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okRejectLot = rest.post("/api/lots/reject", (req, res, ctx) => {
  Data.set("lot-details", (details: LotDetails) => {
    details.lot.lot_status = LotStatus.Rejected
    details.lot.correction_status = CorrectionStatus.NoProblem
  })
  return res(ctx.json({ status: "success" }))
})

export const okAcceptBlending = rest.post(
  "/api/lots/accept-blending",
  (req, res, ctx) => {
    Data.set("lot-details", (details: LotDetails) => {
      details.lot.lot_status = LotStatus.Accepted
      details.lot.delivery_type = DeliveryType.Blending
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okCommentLot = rest.post("/api/lots/comment", (req, res, ctx) => {
  Data.set("lot-details", (details: LotDetails) => {
    details.comments.push({
      entity: producer,
      user: "producer@test.com",
      comment_type: "REGULAR",
      comment_dt: "2021-11-30T16:02:45.832791+01:00",
      // @ts-ignore
      comment: (req._body as FormData).get("comment")?.toString() ?? "error",
    })
  })
  return res(ctx.json({ status: "success" }))
})

export default setupServer(
  okLotDetails,
  okUpdateLot,
  okSendLot,
  okDeleteLot,
  okRequestFix,
  okMarkAsFixed,
  okRejectLot,
  okAcceptBlending,
  okCommentLot,

  okDynamicSettings,
  okDeliverySites,
  okBiocarburantsSearch,
  okMatierePremiereSearch,
  okEntitySearch,
  okCountrySearch,
  okDeliverySitesSearch,
  okProductionSitesSearch
)
