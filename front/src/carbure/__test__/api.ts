import { http, HttpResponse } from "msw"
import translations from "../../../public/locales/fr/translation.json"
import errors from "../../../public/locales/fr/errors.json"
import fields from "../../../public/locales/fr/fields.json"
import { EntityType, NotificationType } from "carbure/types"

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
} from "./data"
import { mockGetWithResponseData } from "./helpers"

export const okStats = http.get("/api/home-stats", () => {
  return HttpResponse.json({
    status: "success",
    data: {
      total_volume: 1000000,
      entities: {
        [EntityType.Operator]: 25,
        [EntityType.Producer]: 25,
        [EntityType.Trader]: 25,
      },
    },
  })
})

export const okNotifications = http.get("/api/entity/notifications", () => {
  return HttpResponse.json({
    status: "success",
    data: [
      {
        id: 1,
        dest: operator,
        datetime: "2024-01-01",
        type: NotificationType.CertificateExpired,
        acked: false,
        send_by_email: false,
        email_sent: false,
        meta: {
          certificate: "1234567890",
        },
      },
      {
        id: 2,
        dest: operator,
        datetime: "2024-01-01",
        acked: true,
        send_by_email: false,
        email_sent: false,
        type: NotificationType.LotsUpdatedByAdmin,
        meta: {
          updated: 10,
          comment: "Commentaire de l'admin",
        },
      },
    ],
  })
})

export const okEntitySearch = http.get("/api/resources/entities", () => {
  return HttpResponse.json({
    status: "success",
    data: [producer, trader, operator],
  })
})

export const okCountrySearch = http.get("/api/resources/countries", () => {
  return HttpResponse.json({
    status: "success",
    data: [country],
  })
})

export const okBiocarburantsSearch = http.get("/api/resources/biofuels", () => {
  return HttpResponse.json({
    status: "success",
    data: [biocarburant],
  })
})

export const okMatierePremiereSearch = http.get(
  "/api/resources/feedstocks",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [matierePremiere],
    })
  }
)

export const okProductionSitesSearch = http.get(
  "/api/resources/production-sites",
  () => {
    return HttpResponse.json({
      status: "success",
      data: [productionSite],
    })
  }
)

export const okDeliverySitesSearch = http.get("/api/resources/depots", () => {
  return HttpResponse.json({
    status: "success",
    data: [deliverySite],
  })
})

export const okTranslations = http.get(
  "/app/locales/fr/translations.json",
  () => {
    return HttpResponse.json({ translations })
  }
)

export const okErrorsTranslations = http.get(
  "/app/locales/fr/errors.json",
  () => {
    return HttpResponse.json({ errors })
  }
)

export const okFieldsTranslations = http.get(
  "/app/locales/fr/fields.json",
  () => {
    return HttpResponse.json({ fields })
  }
)

export const okUnauthorizedUser = http.get("/api/user", () => {
  return new HttpResponse(null, { status: 401 })
})

export const okDefaultUser = mockGetWithResponseData(
  "/user",
  generateUser(EntityType.Administration)
)
