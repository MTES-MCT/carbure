import { rest } from "msw"
import { setupServer } from "msw/node"

import { OwnershipType } from "common/types"

import {
  dbsCertificate,
  deliverySite,
  isccCertificate,
  operator,
  producer,
  productionSite,
} from "common/__test__/data"
import {
  okCountrySearch,
  okDeliverySitesSearch,
  okISCCSearch,
  ok2BSSearch,
} from "common/__test__/api"
import { clone } from "common/__test__/helpers"

let entity = producer
let deliverySites: any[] = []
let productionSites: any[] = []
let isccCertificates: any[] = []
let dbsCertificates: any[] = []

export function setEntity(nextEntity: any) {
  entity = clone(nextEntity)
}

export function setDeliverySites(nextDeliverySites: any[]) {
  deliverySites = nextDeliverySites.map((ds) => ({
    depot: clone(ds),
    ownership_type: OwnershipType.ThirdParty,
  }))
}

export function setProductionSites(nextProductionSites: any[]) {
  productionSites = clone(nextProductionSites)
}

export function setISCCCertificates(nextISCCCertificates: any[]) {
  isccCertificates = clone(nextISCCCertificates)
}

export function set2BSCertificates(next2BSCertificates: any[]) {
  dbsCertificates = clone(next2BSCertificates)
}

export const okSettings = rest.get("/api/v3/settings", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [
          { entity: producer, rights: "rw" },
          { entity: operator, rights: "rw" },
        ],
        requests: [],
      },
    })
  )
})

export const okEmptySettings = rest.get("/api/v3/settings", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [],
        requests: [],
      },
    })
  )
})

export const okDynamicSettings = rest.get(
  "/api/v3/settings",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: {
          email: "producer@test.com",
          rights: [{ entity, rights: "rw" }],
          requests: [],
        },
      })
    )
  }
)

export const okEnableMac = rest.post(
  "/api/v3/settings/enable-mac",
  (req, res, ctx) => {
    setEntity({
      ...entity,
      has_mac: true,
    })

    return res(ctx.json({ status: "success" }))
  }
)

export const okDisableMac = rest.post(
  "/api/v3/settings/disable-mac",
  (req, res, ctx) => {
    setEntity({
      ...entity,
      has_mac: false,
    })

    return res(ctx.json({ status: "success" }))
  }
)

export const okEnableTrading = rest.post(
  "/api/v3/settings/enable-trading",
  (req, res, ctx) => {
    setEntity({
      ...entity,
      has_trading: true,
    })

    return res(ctx.json({ status: "success" }))
  }
)

export const okDisableTrading = rest.post(
  "/api/v3/settings/disable-trading",
  (req, res, ctx) => {
    setEntity({
      ...entity,
      has_trading: false,
    })

    return res(ctx.json({ status: "success" }))
  }
)

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
        data: isccCertificates,
      })
    )
  }
)

export const okAddISCC = rest.post(
  "/api/v3/settings/add-iscc-certificate",
  (req, res, ctx) => {
    setISCCCertificates([isccCertificate])
    return res(ctx.json({ status: "success" }))
  }
)

export const okDeleteISCC = rest.post(
  "/api/v3/settings/delete-iscc-certificate",
  (req, res, ctx) => {
    setISCCCertificates([])
    return res(ctx.json({ status: "success" }))
  }
)

export const okUpdateISCC = rest.post(
  "/api/v3/settings/update-iscc-certificate",
  (req, res, ctx) => {
    setISCCCertificates([isccCertificate])
    return res(ctx.json({ status: "success" }))
  }
)

export const ok2BS = rest.get(
  "/api/v3/settings/get-2bs-certificates",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: dbsCertificates,
      })
    )
  }
)

export const okAdd2BS = rest.post(
  "/api/v3/settings/add-2bs-certificate",
  (req, res, ctx) => {
    set2BSCertificates([dbsCertificate])
    return res(ctx.json({ status: "success" }))
  }
)

export const okDelete2BS = rest.post(
  "/api/v3/settings/delete-2bs-certificate",
  (req, res, ctx) => {
    set2BSCertificates([])
    return res(ctx.json({ status: "success" }))
  }
)

export const okUpdate2BS = rest.post(
  "/api/v3/settings/update-2bs-certificate",
  (req, res, ctx) => {
    set2BSCertificates([dbsCertificate])
    return res(ctx.json({ status: "success" }))
  }
)

export default setupServer(
  okSettings,
  okEnableMac,
  okDisableMac,
  okEnableTrading,
  okDisableTrading,
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
  okISCC,
  okAddISCC,
  okDeleteISCC,
  okUpdateISCC,
  ok2BS,
  okAdd2BS,
  okDelete2BS,
  okUpdate2BS,
  okDeliverySitesSearch,
  okCountrySearch,
  okISCCSearch,
  ok2BSSearch
)
