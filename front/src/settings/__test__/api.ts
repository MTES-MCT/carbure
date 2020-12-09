import { rest } from "msw"

import { UserRightStatus } from "common/types"
import { producer } from "common/__test__/data"

export const okSettings = rest.get("/api/v3/settings", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: [{ entity: producer, rights: "rw" }],
        requests: [
          {
            entity: producer,
            date: new Date(),
            status: UserRightStatus.Accepted,
          },
        ],
      },
    })
  )
})
