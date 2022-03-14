import api, { Api } from "common-v2/services/api"
import { User } from "./types"

export function getUserSettings() {
  return api.get<Api<User>>("/v3/settings/")
}

export function getNotifications(entity_id: number) {
  return api.get("/notifications", { params: { entity_id } })
}

export function ackNotifications(
  entity_id: number,
  notification_ids: number[]
) {
  return api.post("/notifications/toggle", {
    entity_id,
    notification_ids,
  })
}
