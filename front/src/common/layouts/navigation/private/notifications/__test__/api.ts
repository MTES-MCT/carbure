import { http, HttpResponse } from "msw"
import { notifications } from "./data"

// First time notifications are fetched, they are not acked
export const okNotifications = http.get(
  "/api/entities/notifications",
  () => {
    return HttpResponse.json(notifications)
  },
  {
    once: true,
  }
)

// Second time notifications are fetched, they are acked
export const okNotificationsAcked = http.get(
  "/api/entities/notifications",
  () => {
    return HttpResponse.json(notifications.map((n) => ({ ...n, acked: true })))
  },
  {
    once: true,
  }
)
