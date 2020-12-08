import api from "common/services/api"

export function requestAccess(entity_id: number, comment: string) {
  return api.post("/settings/request-entity-access", {
    entity_id,
    comment,
  })
}
