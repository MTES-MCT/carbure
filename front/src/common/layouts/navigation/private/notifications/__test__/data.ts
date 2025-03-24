import { NotificationType } from "../types"
import { operator } from "common/__test__/data"

export const notifications = [
  {
    id: 1,
    dest: operator,
    datetime: "2024-01-01",
    type: NotificationType.CERTIFICATE_EXPIRED,
    acked: false,
    send_by_email: false,
    email_sent: false,
    meta: {
      certificate: "1234567890",
    },
  },
  {
    id: 2,
    dest: operator,
    datetime: "2024-01-01",
    acked: true,
    send_by_email: false,
    email_sent: false,
    type: NotificationType.LOTS_UPDATED_BY_ADMIN,
    meta: {
      updated: 10,
      comment: "Commentaire de l'admin",
    },
  },
]
