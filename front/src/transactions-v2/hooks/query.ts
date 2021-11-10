import { useMemo } from "react"
import { PaginationManager } from "common-v2/components/pagination"
import { normalizeFilters } from "../components/filters"
import { FilterSelection, LotQuery } from "../types"

function useLotQuery(
  entityID: number,
  status: string,
  year: number,
  filters: FilterSelection,
  pagination: PaginationManager
) {
  const { page, limit } = pagination

  return useMemo<LotQuery>(
    () => ({
      entity_id: entityID,
      year,
      status,
      from_idx: page * limit,
      limit: limit || undefined,
      ...normalizeFilters(filters),
    }),
    [entityID, year, status, filters, page, limit]
  )
}

export default useLotQuery
