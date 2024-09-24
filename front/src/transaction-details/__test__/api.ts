import { http, HttpResponse } from "msw"
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

export const okLotDetails = http.get("/api/transactions/lots/details", () => {
  return HttpResponse.json({
    status: "success",
    data: Data.get("lot-details"),
  })
})

export const okUpdateLot = http.post("/api/transactions/lots/update", () => {
  const details = Data.get("lot-details")
  details.lot.transport_document_reference = "DAETEST UPDATED"
  Data.set("lot-details", details)
  return HttpResponse.json({
    status: "success",
  })
})

export const okSendLot = http.post("/api/transactions/lots/send", () => {
  Data.set("lot-details", (details: LotDetails) => {
    details.lot.lot_status = LotStatus.Pending
  })
  return HttpResponse.json({
    status: "success",
  })
})

export const okDeleteLot = http.post("/api/transactions/lots/delete", () => {
  return HttpResponse.json({
    status: "success",
  })
})

export const okRequestFix = http.post(
  "/api/transactions/lots/request-fix",
  () => {
    Data.set("lot-details", (details: LotDetails) => {
      details.lot.correction_status = CorrectionStatus.InCorrection
    })
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okMarkAsFixed = http.post(
  "/api/transactions/lots/submit-fix",
  () => {
    Data.set("lot-details", (details: LotDetails) => {
      details.lot.correction_status = CorrectionStatus.Fixed
    })
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okRejectLot = http.post("/api/transactions/lots/reject", () => {
  Data.set("lot-details", (details: LotDetails) => {
    details.lot.lot_status = LotStatus.Rejected
    details.lot.correction_status = CorrectionStatus.NoProblem
  })
  return HttpResponse.json({
    status: "success",
  })
})

export const okAcceptBlending = http.post(
  "/api/transactions/lots/accept-blending",
  () => {
    Data.set("lot-details", (details: LotDetails) => {
      details.lot.lot_status = LotStatus.Accepted
      details.lot.delivery_type = DeliveryType.Blending
    })

    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okCommentLot = http.post(
  "/api/transactions/lots/comment",
  async ({ request }) => {
    const body = await request.formData()
    Data.set("lot-details", (details: LotDetails) => {
      details.comments.push({
        entity: producer,
        user: "producer@test.com",
        comment_type: "REGULAR",
        comment_dt: "2021-11-30T16:02:45.832791+01:00",
        comment: body.get("comment")?.toString() ?? "error",
      })
    })
    return HttpResponse.json({
      status: "success",
    })
  }
)

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
