import { useMatch } from "react-router-dom"
import { SafTicketSourceStatus } from "../types"

export function useAutoStatus() {
  const matchView = useMatch("/org/:entity/saf/:year/:view/*")
  const matchStatus = useMatch("/org/:entity/saf/:year/:view/:status")

  if (!matchView) {
    return SafTicketSourceStatus.AVAILABLE
  }

  if (matchView.params.view === "ticket-sources") {
    //TODO afficher la categorie non vide en premier au chargement
    // cf transactions/components/category.tsx -> useAutoCategory
    // if (snapshot.ticket_sources_available > 0)
    //   return SafTicketSourceStatus.Available
    // else if (snapshot.ticket_sources_history > 0)
    //   return SafTicketSourceStatus.History

    const status =
      matchStatus?.params?.status?.toUpperCase() as SafTicketSourceStatus
    return status ?? SafTicketSourceStatus.AVAILABLE
  }

  return SafTicketSourceStatus.AVAILABLE
}
