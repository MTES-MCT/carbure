import { rest } from "msw"
import { setupServer } from "msw/node"

import { Data } from "carbure/__test__/helpers"

import {
  okSettings
} from "settings/__test__/api"
import * as data from "./data"

export const okYears = rest.get("/api/years", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [2021],
    })
  )
})

export const okSnapshot = rest.get("/api/saf-snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.safOperatorSnapshot,
    })
  )
})

export const okFilter = rest.get("/api/saf-tickets-sources/filters", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.safClientFilterOptions,
    })
  )
})


export const okSafCertificates = rest.get("/api/saf-certificates", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: Data.get("saf-snapshot"),
    })
  )
})

export default setupServer(
  okYears,
  okSnapshot,
  okSettings,
  okFilter
)
