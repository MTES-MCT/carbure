import api from "common/services/api"
import { UserRole } from "common/types"

export function requestAccess(
  entity_id: number,
  comment: string,
  role: UserRole
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
