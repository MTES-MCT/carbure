import { rest } from "msw"
import { setupServer } from "msw/node"

import { OwnershipType } from "common/types"

import { deliverySite, producer, productionSite } from "common/__test__/data"
import { okCountrySearch, okDeliverySitesSearch } from "common/__test__/api"

let deliverySites: any[] = []
let productionSites: any[] = []

export function setDeliverySites(nextDeliverySites: any[]) {
  deliverySites = nextDeliverySites.map((ds) => ({
    depot: ds,
    ownership_type: OwnershipType.ThirdParty,
  }))
}

export function setProductionSites(nextProductionSites: any[]) {
  productionSites = nextProductionSites
}

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

export const okAddDeliverySite = rest.post(
  "/api/v3/settings/add-delivery-site",
  (req, res, ctx) => {
    setDeliverySites([deliverySite])
    return res(ctx.json({ status: "success" }))
  }
)

export const okDeleteDeliverySite = rest.post(
  "/api/v3/settings/delete-delivery-site",
  (req, res, ctx) => {
    setDeliverySites([])
    return res(ctx.json({ status: "success" }))
  }
)

export const okProductionSites = rest.get(
  "/api/v3/settings/get-production-sites",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: productionSites,
      })
    )
  }
)

export const okAddProductionSite = rest.post(
  "/api/v3/settings/add-production-site",
  (req, res, ctx) => {
    const body = req.body as FormData

    setProductionSites([
      {
        ...productionSite,
        name: body.get("name") as string,
        date_mise_en_service: body.get("date_mise_en_service") as string,
        site_id: body.get("site_id") as string,
      },
    ])

    return res(ctx.json({ status: "success" }))
  }
)

export const okUpdateProductionSite = rest.post(
  "/api/v3/settings/update-production-site",
  (req, res, ctx) => {
    const body = req.body as FormData

    setProductionSites([
      {
        ...productionSite,
        name: body.get("name") as string,
      },
    ])

    return res(ctx.json({ status: "success" }))
  }
)

export const okDeleteProductionSite = rest.post(
  "/api/v3/settings/delete-production-site",
  (req, res, ctx) => {
    setProductionSites([])
    return res(ctx.json({ status: "success" }))
  }
)

export const okSetBiocarburant = rest.post(
  "/api/v3/settings/set-production-site-biocarburants",
  (req, res, ctx) => res(ctx.json({ status: "success" }))
)

export const okSetMatierePremiere = rest.post(
  "/api/v3/settings/set-production-site-matieres-premieres",
  (req, res, ctx) => res(ctx.json({ status: "success" }))
)

export const okSetCertificates = rest.post(
  "/api/v3/settings/set-production-site-certificates",
  (req, res, ctx) => res(ctx.json({ status: "success" }))
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

export default setupServer(
  okSettings,
  okDeliverySites,
  okAddDeliverySite,
  okDeleteDeliverySite,
  okProductionSites,
  okAddProductionSite,
  okUpdateProductionSite,
  okDeleteProductionSite,
  okSetBiocarburant,
  okSetMatierePremiere,
  okSetCertificates,
  ok2BS,
  okISCC,
  okDeliverySitesSearch,
  okCountrySearch
)
