import { operator } from "common/__test__/data"
import { Entity } from "common/types"
import { http, HttpResponse } from "msw"

export const okFindEligibleTiruertEntities = http.get(
  "/api/resources/entities",
  () => {
    return HttpResponse.json<Entity[]>([operator])
  }
)
