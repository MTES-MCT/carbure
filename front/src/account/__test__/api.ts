import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"

import { UserRightStatus } from "carbure/types"
import { producer, trader } from "carbure/__test__/data"
import { clone } from "carbure/__test__/helpers"
import {
  okEntitySearch,
  okErrorsTranslations,
  okFieldsTranslations,
  okTranslations,
} from "carbure/__test__/api"

let accessRequests: any[] = []

export function setAccessRequests(entities: any[]) {
  accessRequests = entities.map((e) => ({
    entity: clone(e),
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

export default setupServer(
  okSettings,
  okAccessRequest,
  okEntitySearch,
  okTranslations,
  okErrorsTranslations,
  okFieldsTranslations
)
