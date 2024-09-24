import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { okSettings } from "settings/__test__/api"
import * as data from "./data"

export const okYears = http.get("/api/saf/operator/years", () => {
  return HttpResponse.json({
    status: "success",
    data: [2021],
  })
})

export const okSnapshot = http.get("/api/saf/operator/snapshot", () => {
  return HttpResponse.json({
    status: "success",
    data: data.safOperatorSnapshot,
  })
})

export const okFilter = http.get(
  "/api/saf/operator/ticket-sources/filters",
  () => {
    return HttpResponse.json({
      status: "success",
      data: data.safClientFilterOptions,
    })
  }
)

export const okSafTicketSources = http.get(
  "/api/saf/operator/ticket-sources",
  () => {
    return HttpResponse.json({
      status: "success",
      data: data.safTicketSourcesResponse,
    })
  }
)

export const okSafTickets = http.get("/api/saf/operator/tickets", () => {
  return HttpResponse.json({
    status: "success",
    data: data.safTicketsResponse,
  })
})

export default setupServer(
  okYears,
  okSnapshot,
  okSettings,
  okFilter,
  okSafTicketSources,
  okSafTickets
)
