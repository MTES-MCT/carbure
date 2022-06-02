import api, { Api } from "common/services/api"
import { User, Notification } from "./types"

export function getUserSettings() {
  return api.get<Api<User>>("/v3/settings/")
}

export async function getNotifications(entity_id: number) {
  if (entity_id === -1) return
  return api.get<Api<Notification[]>>("/notifications", {
    params: { entity_id },
  })
}

export function ackNotifications(
  entity_id: number,
  notification_ids: number[]
) {
  return api.post("/notifications/ack", {
    entity_id,
    notification_ids,
  })
}
