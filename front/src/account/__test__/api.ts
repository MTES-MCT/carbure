import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"

import { UserRightStatus } from "common/types"
import { producer, trader } from "common/__test__/data"
import { okEntitySearch } from "common/__test__/api"

let accessRequests: any[] = []

export function setAccessRequests(entities: any[]) {
  accessRequests = entities.map((e) => ({
    entity: e,
    date: new Date(),
    status: UserRightStatus.Pending,
  }))
}

export const okSettings = http.get("/api/user", () =>
  HttpResponse.json({
    status: "success",
    data: {
      email: "producer@test.com",
      rights: [{ entity: producer, rights: "rw" }],
      requests: accessRequests,
    },
  })
)

export const okAccessRequest = http.post("/api/user/request-access", () => {
  setAccessRequests([trader])
  return HttpResponse.json({ status: "success" })
})

export default setupServer(okSettings, okAccessRequest, okEntitySearch)
