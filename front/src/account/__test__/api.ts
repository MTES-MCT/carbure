import { rest } from "msw"
import { setupServer } from "msw/node"

import { UserRightStatus } from "common/types"
import { producer, trader } from "common/__test__/data"

let accessRequests = [
  { entity: producer, date: new Date(), status: UserRightStatus.Accepted },
]

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

export const okAccessRequest = rest.post(
  "/api/v3/settings/request-entity-access",
  (req, res, ctx) => {
    accessRequests = [
      ...accessRequests,
      { entity: trader, date: new Date(), status: UserRightStatus.Pending },
    ]

    return res(ctx.json({ status: "success" }))
  }
)

export default setupServer(okSettings, okEntitySearch, okAccessRequest)
