import { useMatch } from "react-router-dom"

import { SafTicketStatus } from "saf/types"

export function useAutoStatus() {
  const matchView = useMatch("/org/:entity/saf/:year/:view/*")
  const matchStatus = useMatch("/org/:entity/saf/:year/:view/:status")

  if (!matchView) {
    return SafTicketStatus.PENDING
  }

  if (
    matchView.params.view === "tickets-assigned" ||
    matchView.params.view === "tickets-received"
  ) {
    const status = matchStatus?.params?.status?.toUpperCase() as SafTicketStatus
    return status ?? SafTicketStatus.PENDING
  }

  return SafTicketStatus.PENDING
}
