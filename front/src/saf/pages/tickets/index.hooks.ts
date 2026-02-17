import { useQueryBuilder } from "common/hooks/query-builder-2"
import { useMemo } from "react"
import { useMatch } from "react-router-dom"

import {
  SafTicketQueryBuilder,
  SafTicketStatus,
  SafTicketType,
} from "saf/types"

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
    const status = matchStatus?.params?.status?.toUpperCase()
    if (status == "ALL") return undefined
    return (status as SafTicketStatus) ?? SafTicketStatus.PENDING
  }

  return SafTicketStatus.PENDING
}

export const useSafTicketsQueryBuilder = ({
  type,
  year,
}: {
  type: SafTicketType
  year: number
}) => {
  const status = useAutoStatus()
  const {
    query: _query,
    state,
    actions,
  } = useQueryBuilder<SafTicketQueryBuilder["config"]>({
    status,
    year,
  })

  const query = useMemo(
    () => ({
      ..._query,
      status,
      type,
    }),
    [_query, type, status]
  )

  return { query, state, actions }
}
