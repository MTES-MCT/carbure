import { useMemo } from "react"
import { PaginationManager } from "common-v2/components/pagination"
import { Filter, FilterSelection } from "../types"
import { Entity } from "carbure/types"

export interface StockQuery {
  entity_id: number
  query?: string
  order_by?: string
  direction?: string
  from_idx?: number
  limit?: number
  history?: boolean
  [Filter.Feedstocks]?: string[]
  [Filter.Biofuels]?: string[]
  [Filter.Periods]?: string[]
  [Filter.CountriesOfOrigin]?: string[]
  [Filter.Suppliers]?: string[]
  [Filter.ProductionSites]?: string[]
  [Filter.DeliverySites]?: string[]
}

export interface StockQueryParams {
  entity: Entity
  category: string
  search: string | undefined
  pagination: PaginationManager
  filters: FilterSelection
}

export function useStockQuery({
  entity,
  category,
  search,
  pagination,
  filters,
}: StockQueryParams) {
  const { page = 0, limit } = pagination

  return useMemo<StockQuery>(
    () => ({
      entity_id: entity.id,
      history: category === "history" ? true : undefined,
      query: search ? search : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      ...filters,
    }),
    [entity.id, category, search, page, limit, filters]
  )
}

export default useStockQuery
