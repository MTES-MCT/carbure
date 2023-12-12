import { rest } from "msw"
import { setupServer } from "msw/node"

import { OwnershipType } from "carbure/types"

import {
  okCountrySearch,
  okDeliverySitesSearch,
  okErrorsTranslations,
  okFieldsTranslations,
  okProductionSitesSearch,
  okTranslations,
} from "carbure/__test__/api"
import {
  deliverySite,
  entityRequest,
  entityRight,
  entityRights,
  operator,
  producer,
  productionSite,
} from "carbure/__test__/data"
import { clone, Data } from "carbure/__test__/helpers"
import { dcApplicationErrors } from "./data"
import { elecChargingPointsApplicationCheckResponseFailed, elecChargingPointsApplicationCheckResponseSucceed, elecChargingPointsApplications } from "elec/__test__/data"

let deliverySites: any[] = []
let productionSites: any[] = []

const mockGetWithResponseData = (url: string, data: any) => {
  return rest.get(url, (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data,
      })
    )
  })
}
const mockPostWithResponseData = (url: string, data?: any, withError: boolean = false) => {
  return rest.post(url, (req, res, ctx) => {
    return res(
      withError ? ctx.status(400) : ctx.status(200),
      ctx.json({
        status: withError ? "error" : "success",
        data,
      })
    )
  })
}





export function setEntity(nextEntity: any) {
  Data.set("entity", nextEntity)
}
setEntity(producer)

export function setDeliverySites(nextDeliverySites: any[]) {
  deliverySites = nextDeliverySites.map((ds) => ({
    depot: clone(ds),
    ownership_type: OwnershipType.ThirdParty,
  }))
}

export function setProductionSites(nextProductionSites: any[]) {
  productionSites = clone(nextProductionSites)
}

export const okSettings = rest.get("/api/user", (req, res, ctx) => {
  const entity = Data.get("entity")
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [
          { ...entityRight, entity },
          { ...entityRight, entity: operator },
        ],
        requests: [
          { ...entityRight, entity },
          { ...entityRequest, entity: operator },
        ],
      },
    })
  )
})

export const okEmptySettings = rest.get("/api/user", (req, res, ctx) => {
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

export const okDynamicSettings = rest.get("/api/user", (req, res, ctx) => {
  const entity = Data.get("entity")

  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [{ ...entityRight, entity }],
        requests: [],
      },
    })
  )
})

export const okEnableMac = rest.post(
  "/api/entity/options/release-for-consumption",
  (req, res, ctx) => {
    const entity = Data.get("entity")
    setEntity({
      ...entity,
      has_mac: true,
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okDisableMac = rest.post(
  "/api/entity/options/release-for-consumption",
  (req, res, ctx) => {
    const entity = Data.get("entity")
    setEntity({
      ...entity,
      has_mac: false,
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okEnableTrading = rest.post(
  "/api/entity/options/trading",
  (req, res, ctx) => {
    const entity = Data.get("entity")
    setEntity({
      ...entity,
      has_trading: true,
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okDisableTrading = rest.post(
  "/api/entity/options/trading",
  (req, res, ctx) => {
    const entity = Data.get("entity")
    setEntity({
      ...entity,
      has_trading: false,
    })
    return res(ctx.json({ status: "success" }))
  }
)

export const okDeliverySites = rest.get(
  "/api/entity/depots",
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
  "/api/entity/depots/add",
  (req, res, ctx) => {
    setDeliverySites([deliverySite])
    return res(ctx.json({ status: "success" }))
  }
)

export const okDeleteDeliverySite = rest.post(
  "/api/entity/depots/delete",
  (req, res, ctx) => {
    setDeliverySites([])
    return res(ctx.json({ status: "success" }))
  }
)

export const okProductionSites = rest.get(
  "/api/entity/production-sites",
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
  "/api/entity/production-sites/add",
  (req, res, ctx) => {
    // @ts-ignore
    const body = req._body as FormData

    const psite = {
      ...productionSite,
      name: body.get("name") as string,
      date_mise_en_service: body.get("date_mise_en_service") as string,
      site_id: body.get("site_id") as string,
    }

    setProductionSites([psite])

    return res(ctx.json({ status: "success", data: psite }))
  }
)

export const okUpdateProductionSite = rest.post(
  "/api/entity/production-sites/update",
  (req, res, ctx) => {
    // @ts-ignore
    const body = req._body as FormData

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
  "/api/entity/production-sites/delete",
  (req, res, ctx) => {
    setProductionSites([])
    return res(ctx.json({ status: "success" }))
  }
)

export const okSetBiocarburant = rest.post(
  "/api/entity/production-sites/set-biofuels",
  (req, res, ctx) => res(ctx.json({ status: "success" }))
)

export const okSetMatierePremiere = rest.post(
  "/api/entity/production-sites/set-feedstocks",
  (req, res, ctx) => res(ctx.json({ status: "success" }))
)

export const okSetCertificates = rest.post(
  "/api/entity/production-sites/set-certificates",
  (req, res, ctx) => res(ctx.json({ status: "success" }))
)

export const okEntityRights = rest.get(
  "http://localhost/api/entity/users",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: entityRights }))
  }
)

export const okSelfCertificates = rest.get(
  "/api/entity/certificates",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: [] }))
  }
)

export const okDoubleCountApplications = rest.get(
  "/api/double-counting/agreements",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success", data: [] }))
  }
)

export const okDoubleCountUploadApplication = rest.post(
  "/api/v3/doublecount/upload",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: { dca_id: 142332 },
      })
    )
  }
)

export const okDoubleCountUploadAgreements = mockGetWithResponseData("/api/double-counting/agreements", [])


export const okDoubleCountUploadDocumentation = rest.post(
  "/api/v3/doublecount/upload-documentation",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: { dca_id: 142332 },
      })
    )
  }
)

export const koDoubleCountUploadApplication = rest.post(
  "/api/v3/doublecount/upload",
  (req, res, ctx) => {
    return res(
      ctx.status(400),
      ctx.json({
        status: "error",
        error: "DOUBLE_COUNTING_IMPORT_FAILED",
        data: dcApplicationErrors,
      })
    )
  }
)


export const okChargingPointsApplications = rest.get("/api/elec/cpo/charging-points/applications", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: elecChargingPointsApplications,
    })
  )
})

export const okChargingPointsApplicationsEmpty = mockGetWithResponseData("/api/elec/cpo/charging-points/applications", [])
export const okChargingPointsCheckValid = mockPostWithResponseData("/api/elec/cpo/charging-points/check-application", elecChargingPointsApplicationCheckResponseSucceed)
export const okChargingPointsCheckError = mockPostWithResponseData("/api/elec/cpo/charging-points/check-application", elecChargingPointsApplicationCheckResponseFailed, true)
export const okChargingPointsAddSuccess = mockPostWithResponseData("/api/elec/cpo/charging-points/add-application")




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
  okProductionSitesSearch,
  okAddProductionSite,
  okUpdateProductionSite,
  okDeleteProductionSite,
  okSetBiocarburant,
  okSetMatierePremiere,
  okSetCertificates,
  okDeliverySitesSearch,
  okCountrySearch,
  okEntityRights,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations,
  okSelfCertificates,
  okDoubleCountApplications,
  okDoubleCountUploadAgreements,
  okChargingPointsApplications,
  okChargingPointsCheckValid,
  okChargingPointsAddSuccess
)
