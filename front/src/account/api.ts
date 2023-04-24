import api from "common/services/api"
import { UserRole } from "carbure/types"

export function requestAccess(
  entity_id: number,
  role: UserRole,
  comment: string = ""
) {
  return api.post("/v5/user/request-access", {
    entity_id,
    comment,
    role,
  })
}

export function revokeMyself(entity_id: number) {
  return api.post("/v5/user/revoke-access", { entity_id })
}
