import { rest } from "msw"

import {
  country,
  deliverySite,
  isccCertificate,
  expiredISCCCertificate,
  dbsCertificate,
  expired2BSCertificate,
  producer,
  trader,
  operator,
  matierePremiere,
  biocarburant,
  productionSite,
  redcertCertificate,
  expiredRedcertCertificate,
} from "common/__test__/data"

export const okEntitySearch = rest.get(
  "/api/v3/common/entities",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [producer, trader, operator],
      })
    )
  }
)

export const okCountrySearch = rest.get(
  "/api/v3/common/countries",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [country],
      })
    )
  }
)

export const okBiocarburantsSearch = rest.get(
  "/api/v3/common/biocarburants",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [biocarburant],
      })
    )
  }
)

export const okMatierePremiereSearch = rest.get(
  "/api/v3/common/matieres-premieres",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [matierePremiere],
      })
    )
  }
)

export const okProductionSitesSearch = rest.get(
  "/api/v3/common/production-sites",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [productionSite],
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

export const okISCCSearch = rest.get(
  "/api/v3/common/iscc-certificates",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [isccCertificate, expiredISCCCertificate],
      })
    )
  }
)

export const ok2BSSearch = rest.get(
  "/api/v3/common/2bs-certificates",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [dbsCertificate, expired2BSCertificate],
      })
    )
  }
)

export const okRedcertSearch = rest.get(
  "/api/v3/common/redcert-certificates",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [redcertCertificate, expiredRedcertCertificate],
      })
    )
  }
)
