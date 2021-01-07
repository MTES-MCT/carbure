import { rest } from "msw"
import { setupServer } from "msw/node"

import { UserRightStatus } from "common/types"
import { producer, trader } from "common/__test__/data"
import { okEntitySearch } from "common/__test__/api"
import { clone } from "common/__test__/helpers"

let accessRequests: any[] = []

export function setAccessRequests(entities: any[]) {
  accessRequests = entities.map((e) => ({
    entity: clone(e),
    date: new Date(),
    status: UserRightStatus.Pending,
  }))
}

export const okSettings = rest.get("/api/v3/settings", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [{ entity: producer, rights: "rw" }],
        requests: accessRequests,
      },
    })
  )
})

export const okAccessRequest = rest.post(
  "/api/v3/settings/request-entity-access",
  (req, res, ctx) => {
    setAccessRequests([trader])
    return res(ctx.json({ status: "success" }))
  }
)

export default setupServer(okSettings, okAccessRequest, okEntitySearch)
