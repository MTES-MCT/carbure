import api, { Api } from "common/services/api"
import { EntityRights } from "settings/types"
import { UserRole } from 'carbure/types';

export function getEntityRights(entity_id: number) {
  return api.get<Api<EntityRights>>("/v5/entity/users", {
    params: { entity_id },
  })
}

export function revokeUserRights(entity_id: number, email: string) {
  return api.post("/v5/entity/users/revoke-access", { entity_id, email })
}

export function acceptUserRightsRequest(entity_id: number, request_id: number) {
  return api.post("/v5/entity/users/grant-access", { entity_id, request_id })
}

export function changeUserRole(entity_id: number, email: string, role: UserRole) {
  return api.post("/v5/entity/users/change-role", { entity_id, email, role })
}