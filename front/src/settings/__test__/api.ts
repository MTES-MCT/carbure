import { rest } from "msw"
import { setupServer } from "msw/node"

import { OwnershipType } from "common/types"
import { deliverySite, producer } from "common/__test__/data"

export const okSettings = rest.get("/api/v3/settings", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [{ entity: producer, rights: "rw" }],
        requests: [],
      },
    })
  )
})

let deliverySites: any[] = []

export const okDeliverySites = rest.get(
  "/api/v3/settings/get-delivery-sites",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: deliverySites,
      })
    )
  }
)

export const okProductionSites = rest.get(
  "/api/v3/settings/get-production-sites",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [],
      })
    )
  }
)

export const okISCC = rest.get(
  "/api/v3/settings/get-iscc-certificates",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [],
      })
    )
  }
)

export const ok2BS = rest.get(
  "/api/v3/settings/get-2bs-certificates",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [],
      })
    )
  }
)

export const okDeliverySitesSearch = rest.get(
  "/api/v3/common/delivery-sites",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [deliverySite],
      })
    )
  }
)

export const okAddDeliverySites = rest.post(
  "/api/v3/settings/add-delivery-site",
  (req, res, ctx) => {
    deliverySites = [
      ...deliverySites,
      {
        depot: deliverySite,
        ownership_type: OwnershipType.ThirdParty,
      },
    ]

    return res(ctx.json({ status: "success" }))
  }
)

export default setupServer(
  okSettings,
  okAddDeliverySites,
  okDeliverySites,
  okDeliverySitesSearch,
  ok2BS,
  okISCC,
  okProductionSites
)
