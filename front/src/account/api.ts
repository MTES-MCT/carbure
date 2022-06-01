import api from "common-v2/services/api"
import { UserRole } from "carbure/types"

export function requestAccess(
  entity_id: number,
  role: UserRole,
  comment: string = ""
) {
  return api.post("/settings/request-entity-access", {
    entity_id,
    comment,
    role,
  })
}

export function revokeMyself(entity_id: number) {
  return api.post("/settings/revoke-myself", { entity_id })
}
