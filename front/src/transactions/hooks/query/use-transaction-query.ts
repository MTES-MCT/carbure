import { LotStatus, TransactionQuery } from "common/types"
import { useMemo } from "react"
import { FilterSelection } from "./use-filters"

export default function useTransactionQuery(
  status: LotStatus,
  entityID: number,
  filters: FilterSelection["selected"],
  year: number,
  page: number,
  limit: number | null,
  query: string,
  sortBy: string,
  order: string,
  invalid: boolean,
  deadline: boolean
): TransactionQuery {
  return useMemo(
    () => ({
      ...filters,
      entity_id: entityID,
      from_idx: limit ? page * limit : 0,
      sort_by: sortBy,
      status,
      year,
      limit,
      query,
      order,
      invalid,
      deadline,
    }),
    [
      filters,
      entityID,
      sortBy,
      status,
      year,
      page,
      limit,
      query,
      order,
      invalid,
      deadline,
    ]
  )
}
