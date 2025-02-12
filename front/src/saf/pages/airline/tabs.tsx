import { useMatch } from "react-router-dom"

import { SafAirlineSnapshot, SafTicketStatus } from "saf/types"

export interface StatusTabsProps {
  loading: boolean
  count?: SafAirlineSnapshot
}

export function useAutoStatus() {
  const matchStatus = useMatch("/org/:entity/saf/:year/tickets/:status/*")
  const status = matchStatus?.params.status as SafTicketStatus
  return (status.toUpperCase() as SafTicketStatus) ?? SafTicketStatus.PENDING
}
