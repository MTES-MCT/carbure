import { rest } from "msw"
import translations from "../../../public/locales/fr/translation.json"
import errors from "../../../public/locales/fr/errors.json"
import fields from "../../../public/locales/fr/fields.json"

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

export const okTranslations = rest.get(
  "/v2/locales/fr/translations.json",
  (req, res, ctx) => {
    return res(ctx.json(translations))
  }
)

export const okErrorsTranslations = rest.get(
  "/v2/locales/fr/errors.json",
  (req, res, ctx) => {
    return res(ctx.json(errors))
  }
)

export const okFieldsTranslations = rest.get(
  "/v2/locales/fr/fields.json",
  (req, res, ctx) => {
    return res(ctx.json(fields))
  }
)
