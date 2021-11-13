import { useMemo } from "react"
import { PaginationManager } from "common-v2/components/pagination"
import { FilterSelection, LotQuery } from "../types"

function useLotQuery(
  entityID: number,
  status: string,
  year: number,
  query: string | undefined,
  invalid: boolean,
  deadline: boolean,
  pagination: PaginationManager,
  filters: FilterSelection
) {
  const { page = 0, limit } = pagination

  return useMemo<LotQuery>(
    () => ({
      entity_id: entityID,
      year,
      status,
      query: query ? query : undefined,
      invalid: invalid ? true : undefined,
      deadline: deadline ? true : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      ...filters,
    }),
    [entityID, year, status, query, invalid, deadline, page, limit, filters]
  )
}

export default useLotQuery
