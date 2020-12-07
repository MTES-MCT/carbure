import { useEffect } from "react"
import { Lots } from "common/types"
import useAPI from "common/hooks/helpers/use-api"
import { getStocks, getStockSnapshot } from "../api"
import { EntitySelection } from "carbure/hooks/use-entity"
import { PageSelection } from "common/components/pagination"
import { FilterSelection } from "common/hooks/query/use-filters"
import { SearchSelection } from "common/hooks/query/use-search"
import { SortingSelection } from "common/hooks/query/use-sort-by"
import { StatusSelection } from "common/hooks/query/use-status"

export interface StockHook {
  loading: boolean
  error: string | null
  data: Lots | null
  getStock: () => void
  exportAllTransactions: () => void
}

export function useGetStockSnapshot(entity: EntitySelection) {
  const [snapshot, resolveStockSnapshot] = useAPI(getStockSnapshot)

  function getSnapshot() {
    if (entity !== null) {
      return resolveStockSnapshot(entity.id).cancel
    }
  }

  useEffect(getSnapshot, [resolveStockSnapshot, entity])

  return { ...snapshot, getSnapshot }
}

// fetches current transaction list when parameters change
export function useGetStocks(
  entity: EntitySelection,
  filters: FilterSelection,
  status: StatusSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection
): StockHook {
  const [stock, resolveStocks] = useAPI(getStocks)
  const entityID = entity?.id

  function exportAllTransactions() {
    return null
  }

  function getStock() {
    if (entityID !== null) {
      return resolveStocks(
        entityID,
        filters.selected,
        status.active,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order
      ).cancel
    }
  }

  useEffect(getStock, [
    resolveStocks,
    entityID,
    filters.selected,
    status.active,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
  ])

  return { ...stock, getStock, exportAllTransactions }
}
