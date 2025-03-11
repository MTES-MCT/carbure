import { http, HttpResponse } from "msw"
import { apiTypes } from "common/services/api-fetch.types"
import * as data from "./data"

export const okSafTicketSourceDetails = http.get(
  "/api/saf/ticket-sources/:id",
  () => HttpResponse.json(data.safTicketSourceDetails)
)

export const okFindClients = http.get("/api/saf/clients/", () =>
  HttpResponse.json<apiTypes["PaginatedEntityPreviewList"]>({
    count: data.safClients.length,
    results: data.safClients,
  })
)

export const assignSafTicket = http.post<
  object,
  apiTypes["SafTicketSourceAssignmentRequest"],
  apiTypes["SafTicketSourceAssignment"]
>("/api/saf/ticket-sources/:id/assign/", async ({ request }) => {
  const formData = await request.formData()

  const body = Object.fromEntries(
    formData.entries()
  ) as unknown as apiTypes["SafTicketSourceAssignmentRequest"]

  return HttpResponse.json({
    assignment_period: body.assignment_period,
    client_id: body.client_id,
    volume: body.volume,
  })
})
