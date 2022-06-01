import api, { Api } from "common-v2/services/api"
import { EntityRights } from "settings/types"

export function getEntityRights(entity_id: number) {
  return api.get<Api<EntityRights>>("/v3/settings/get-entity-rights", {
    params: { entity_id },
  })
}

export function revokeUserRights(entity_id: number, email: string) {
  return api.post("/v3/settings/revoke-user", { entity_id, email })
}

export function acceptUserRightsRequest(entity_id: number, request_id: number) {
  return api.post("/v3/settings/accept-user", { entity_id, request_id })
}
