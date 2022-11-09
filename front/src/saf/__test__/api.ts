import { rest } from "msw"
import { setupServer } from "msw/node"

import { Data } from "carbure/__test__/helpers"

import {
  okSettings
} from "settings/__test__/api"
import * as data from "./data"

export const okYears = rest.get("/api/v5/saf/operator/years", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [2021],
    })
  )
})

export const okSnapshot = rest.get("/api/v5/saf/operator/snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.safOperatorSnapshot,
    })
  )
})

export const okFilter = rest.get("/api/v5/saf/operator/ticket-sources/filters", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.safClientFilterOptions,
    })
  )
})

export const okSafTicketSources = rest.get("/api/v5/saf/operator/ticket-sources", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.safTicketSourcesResponse,
    })
  )
})

export const okSafTickets = rest.get("/api/v5/saf/operator/tickets", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: data.safTicketsResponse,
    })
  )
})

export default setupServer(
  okYears,
  okSnapshot,
  okSettings,
  okFilter,
  okSafTicketSources,
  okSafTickets
)
