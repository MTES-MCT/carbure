import { useMemo } from "react"
import { normalizeFilters } from "../components/filters"
import { FilterSelection, LotQuery } from "../types"

function useLotQuery(
  entityID: number,
  status: string,
  year: number,
  filters: FilterSelection
) {
  return useMemo<LotQuery>(
    () => ({
      entity_id: entityID,
      year,
      status,
      ...normalizeFilters(filters),
    }),
    [entityID, year, status, filters]
  )
}

export default useLotQuery
