import api, { Api } from "common-v2/services/api"
import { User, Notification } from "./types"

export function getUserSettings() {
  return api.get<Api<User>>("/v3/settings/")
}

export function getNotifications(entity_id: number) {
  return api.get<Api<Notification[]>>("/notifications", { params: { entity_id } })
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
