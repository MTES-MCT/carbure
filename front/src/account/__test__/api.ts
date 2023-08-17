import { rest } from "msw"
import { setupServer } from "msw/node"

import { UserRightStatus } from "carbure/types"
import { trader } from "carbure/__test__/data"
import { clone } from "carbure/__test__/helpers"
import {
  okEntitySearch,
  okErrorsTranslations,
  okFieldsTranslations,
  okTranslations,
} from "carbure/__test__/api"

let accessRights: any[] = []

export function setAccessRequests(entities: any[]) {
  accessRights = entities.map((e) => ({
    entity: clone(e),
    date: new Date(),
    status: UserRightStatus.Pending,
  }))
}

export const okSettings = rest.get("/api/v5/user", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        email: "producer@test.com",
        rights: accessRights,
      },
    })
  )
})

export const okAccessRequest = rest.post(
  "/api/v5/user/request-access",
  (req, res, ctx) => {
    setAccessRequests([trader])
    return res(ctx.json({ status: "success" }))
  }
)

export default setupServer(
  okSettings,
  okAccessRequest,
  okEntitySearch,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations
)
