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
} from "common/__test__/data"

export const okEntitySearch = rest.get(
  "/api/v3/common/entities",
  (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [producer, trader],
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
