import { useMemo } from "react"
import { PaginationManager } from "common-v2/components/pagination"
import { FilterSelection, Status, Filter } from "../types"
import { Entity } from "carbure/types"
import { Order } from "common-v2/components/table"

export interface LotQuery {
  entity_id: number
  status?: string
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
  category: string
  year: number
  search: string | undefined
  invalid: boolean
  deadline: boolean
  pagination: PaginationManager
  order: Order | undefined
  filters: FilterSelection
}

export function useLotQuery({
  entity,
  status,
  category,
  year,
  search,
  invalid,
  deadline,
  pagination,
  order,
  filters,
}: LotQueryParams) {
  const { page = 0, limit } = pagination

  return useMemo<LotQuery>(
    () => ({
      entity_id: entity.id,
      year,
      status: status.toUpperCase(),
      query: search ? search : undefined,
      history: category === "history" ? true : undefined,
      correction: category === "correction" ? true : undefined,
      invalid: invalid ? true : undefined,
      deadline: deadline ? true : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    }),
    [
      entity.id,
      year,
      status,
      category,
      search,
      invalid,
      deadline,
      page,
      limit,
      order,
      filters,
    ]
  )
}

export default useLotQuery
