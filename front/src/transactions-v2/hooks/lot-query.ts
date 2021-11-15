import { useMemo } from "react"
import { PaginationManager } from "common-v2/components/pagination"
import { FilterSelection, Status, Filter } from "../types"
import { Entity } from "carbure/types"

export interface LotQuery {
  entity_id: number
  status?: Status
  year?: number
  query?: string
  order_by?: string
  direction?: string
  from_idx?: number
  limit?: number
  invalid?: boolean
  deadline?: boolean
  history?: boolean
  correction?: boolean
  [Filter.DeliveryStatus]?: string[]
  [Filter.Feedstocks]?: string[]
  [Filter.Biofuels]?: string[]
  [Filter.Periods]?: string[]
  [Filter.CountriesOfOrigin]?: string[]
  [Filter.Suppliers]?: string[]
  [Filter.Clients]?: string[]
  [Filter.ProductionSites]?: string[]
  [Filter.DeliverySites]?: string[]
  [Filter.AddedBy]?: string[]
  [Filter.Errors]?: string[]
  [Filter.Forwarded]?: string[]
  [Filter.Mac]?: string[]
  [Filter.HiddenByAdmin]?: string[]
  [Filter.HiddenByAuditor]?: string[]
  [Filter.ClientTypes]?: string[]
}

export interface LotQueryParams {
  entity: Entity
  status: Status
  sub: string
  year: number
  search: string | undefined
  correction: boolean
  invalid: boolean
  deadline: boolean
  pagination: PaginationManager
  filters: FilterSelection
}

export function useLotQuery({
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
