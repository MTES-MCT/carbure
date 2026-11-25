import { useMatch } from "react-router"
import { SafTicketSourceStatus } from "../../types"

export function useAutoStatus() {
  const matchView = useMatch("/org/:entity/saf/:year/:view/*")
  const matchStatus = useMatch("/org/:entity/saf/:year/:view/:status")

  if (!matchView) {
    return SafTicketSourceStatus.AVAILABLE
  }

  if (matchView.params.view === "ticket-sources") {
    const status =
      matchStatus?.params?.status?.toUpperCase() as SafTicketSourceStatus
    return status ?? SafTicketSourceStatus.AVAILABLE
  }

  return SafTicketSourceStatus.AVAILABLE
}
