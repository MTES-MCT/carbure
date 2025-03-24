import { api as apiFetch } from "common/services/api-fetch"

export async function getNotifications(entity_id: number) {
  if (entity_id === -1) return
  return apiFetch.GET("/entities/notifications/", {
    params: { query: { entity_id } },
  })
}

export function ackNotifications(
  entity_id: number,
  notification_ids: number[]
) {
  return apiFetch.POST("/entities/notifications/ack/", {
    params: { query: { entity_id } },
    body: { notification_ids },
  })
}
