import { useMemo } from "react"
import { PaginationManager } from "common-v2/components/pagination"
import { FilterSelection, LotQuery } from "../types"
import { Entity } from "carbure/types"

export interface LotQueryParams {
  entity: Entity
  status: string
  sub: string
  year: number
  search: string | undefined
  correction: boolean
  invalid: boolean
  deadline: boolean
  pagination: PaginationManager
  filters: FilterSelection
}

function useLotQuery({
  entity,
  status,
  sub,
  year,
  search,
  correction,
  invalid,
  deadline,
  pagination,
  filters,
}: LotQueryParams) {
  const { page = 0, limit } = pagination

  return useMemo<LotQuery>(
    () => ({
      entity_id: entity.id,
      year,
      status,
      query: search ? search : undefined,
      history: sub === "history" ? true : undefined,
      correction: correction ? true : undefined,
      invalid: invalid ? true : undefined,
      deadline: deadline ? true : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      ...filters,
    }),
    [
      entity.id,
      year,
      status,
      sub,
      search,
      correction,
      invalid,
      deadline,
      page,
      limit,
      filters,
    ]
  )
}

export default useLotQuery
