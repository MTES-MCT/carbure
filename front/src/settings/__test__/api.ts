import { http, HttpResponse } from "msw"
import { OwnershipType } from "carbure/types"

import {
  deliverySite,
  entityRequest,
  entityRight,
  entityRights,
  operator,
  producer,
  productionSite,
} from "carbure/__test__/data"
import {
  Data,
  clone,
  mockGetWithResponseData,
  mockPostWithResponseData,
  setEntity,
} from "carbure/__test__/helpers"
import { dcApplicationErrors } from "./data"

let deliverySites: any[] = []
let productionSites: any[] = []

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

export const okSettings = http.get("/api/user", () => {
  const entity = Data.get("entity")

  return HttpResponse.json({
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
})

export const okEmptySettings = http.get("/api/user", () => {
  return HttpResponse.json({
    status: "success",
    data: {
      email: "producer@test.com",
      rights: [],
      requests: [],
    },
  })
})

export const okDynamicSettings = http.get("/api/user", () => {
  const entity = Data.get("entity")

  return HttpResponse.json({
    status: "success",
    data: {
      email: "producer@test.com",
      rights: [{ ...entityRight, entity }],
      requests: [],
    },
  })
})

export const okEnableMac = http.post(
  "/api/entities/release-for-consumption/",
  () => {
    const entity = Data.get("entity")
    setEntity({
      ...entity,
      has_mac: true,
    })
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okDisableMac = http.post(
  "/api/entities/release-for-consumption/",
  () => {
    const entity = Data.get("entity")
    setEntity({
      ...entity,
      has_mac: false,
    })
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okEnableTrading = http.post("/api/entities/trading/", () => {
  const entity = Data.get("entity")
  setEntity({
    ...entity,
    has_trading: true,
  })
  return HttpResponse.json({
    status: "success",
  })
})

export const okDisableTrading = http.post("/api/entities/trading/", () => {
  const entity = Data.get("entity")
  setEntity({
    ...entity,
    has_trading: false,
  })
  return HttpResponse.json({
    status: "success",
  })
})

export const okDeliverySites = http.get("/api/entities/depots/delete/", () => {
  return HttpResponse.json({
    status: "success",
    data: deliverySites,
  })
})

export const okAddDeliverySite = http.post("/api/entities/depots/add/", () => {
  setDeliverySites([deliverySite])
  return HttpResponse.json({
    status: "success",
  })
})

export const okCreateNewDeliverySite = http.post(
  "/entities/depots/create/",
  () => {
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okDeleteDeliverySite = http.post(
  "/api/entities/depots/delete/",
  () => {
    setDeliverySites([])
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okProductionSites = http.get(
  "/api/entities/production-sites/",
  () => {
    return HttpResponse.json({
      status: "success",
      data: productionSites,
    })
  }
)

export const okAddProductionSite = http.post(
  "/api/entities/production-sites/add/",
  async ({ request }) => {
    const body = (await request.json()) as FormData

    const psite = {
      ...productionSite,
      name: body.get("name") as string,
      date_mise_en_service: body.get("date_mise_en_service") as string,
      site_id: body.get("site_id") as string,
    }

    setProductionSites([psite])

    return HttpResponse.json({
      status: "success",
      data: psite,
    })
  }
)

export const okUpdateProductionSite = http.post(
  "/api/entities/production-sites/update/",
  async ({ request }) => {
    const body = (await request.json()) as FormData

    setProductionSites([
      {
        ...productionSite,
        name: body.get("name") as string,
      },
    ])

    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okDeleteProductionSite = http.post(
  "/api/entities/production-sites/delete/",
  () => {
    setProductionSites([])
    return HttpResponse.json({
      status: "success",
    })
  }
)

export const okSetBiocarburant = http.post(
  "/api/entities/production-sites/set-biofuels/",
  () =>
    HttpResponse.json({
      status: "success",
    })
)

export const okSetMatierePremiere = http.post(
  "/api/entities/production-sites/set-feedstocks/",
  () =>
    HttpResponse.json({
      status: "success",
    })
)

export const okSetCertificates = http.post(
  "/api/entities/production-sites/set-certificates/",
  () =>
    HttpResponse.json({
      status: "success",
    })
)

export const okEntityRights = http.get(
  "http://localhost/api/entities/users/",
  () => {
    return HttpResponse.json({
      status: "success",
      data: entityRights,
    })
  }
)

export const okInviteUser = mockPostWithResponseData(
  "/entities/users/invite/",
  {
    email: "test@test.com",
    rights: [{ entity: producer, rights: "rw" }],
    requests: [],
  }
)

export const okSelfCertificates = http.get(
  "/api/entities/certificates/",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [],
    })
  }
)

export const okDoubleCountApplications = http.get(
  "/api/double-counting/agreements",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [],
    })
  }
)

export const okDoubleCountUploadApplication = http.post(
  "/api/v3/doublecount/upload",
  () => {
    return HttpResponse.json({
      status: "success",
      data: { dca_id: 142332 },
    })
  }
)

export const okDoubleCountUploadAgreements = mockGetWithResponseData(
  "/double-counting/agreements",
  []
)

export const okDoubleCountUploadDocumentation = http.post(
  "/api/v3/doublecount/upload-documentation",
  () => {
    return HttpResponse.json({
      status: "success",
      data: { dca_id: 142332 },
    })
  }
)

export const koDoubleCountUploadApplication = http.post(
  "/api/v3/doublecount/upload",
  () => {
    return HttpResponse.json(
      {
        status: "error",
        error: "DOUBLE_COUNTING_IMPORT_FAILED",
        data: dcApplicationErrors,
      },
      {
        status: 400,
      }
    )
  }
)

const mockedEndpoints = {
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
  okEntityRights,
  okSelfCertificates,
  okDoubleCountApplications,
  okDoubleCountUploadAgreements,
}

export default mockedEndpoints
