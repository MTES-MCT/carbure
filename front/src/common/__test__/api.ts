import { http as mswHttp, HttpResponse } from "msw"
import { EntityType } from "common/types"

import {
  country,
  deliverySite,
  producer,
  trader,
  operator,
  matierePremiere,
  biocarburant,
  productionSite,
  generateUser,
  entitySite,
} from "./data"
import { mockGetWithResponseData } from "./helpers"
import { http } from "./http"

export const okEntitySearch = http.get("/resources/entities", () => {
  return HttpResponse.json([producer, trader, operator])
})

export const okCountrySearch = mswHttp.get("/api/resources/countries", () => {
  return HttpResponse.json([country])
})

export const okBiocarburantsSearch = mswHttp.get(
  "/api/resources/biofuels",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [biocarburant],
    })
  }
)

export const okMatierePremiereSearch = mswHttp.get(
  "/api/resources/feedstocks",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [matierePremiere],
    })
  }
)

export const okProductionSitesSearch = mswHttp.get(
  "/api/resources/production-sites",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [productionSite],
    })
  }
)

export const okGetDeliverySites = mswHttp.get("/api/entities/depots", () => {
  return HttpResponse.json([entitySite])
})

export const okDeliverySitesSearch = mswHttp.get(
  "/api/resources/depots",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [deliverySite],
    })
  }
)

export const okUnauthorizedUser = mswHttp.get("/api/user", () => {
  return new HttpResponse(null, { status: 401 })
})

export const okDefaultUser = mockGetWithResponseData(
  "/user",
  generateUser(EntityType.Administration)
)
