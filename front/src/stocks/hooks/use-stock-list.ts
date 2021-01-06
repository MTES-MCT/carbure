import { useEffect } from "react"
import { Lots } from "common/types"
import useAPI from "common/hooks/use-api"
import { getStocks, getStockSnapshot } from "../api"
import { EntitySelection } from "carbure/hooks/use-entity"
import { PageSelection } from "common/components/pagination"
import { FilterSelection } from "transactions/hooks/query/use-filters"
import { SearchSelection } from "transactions/hooks/query/use-search"
import { SortingSelection } from "transactions/hooks/query/use-sort-by"
import { StatusSelection } from "transactions/hooks/query/use-status"

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
      resolveStockSnapshot(entity.id)
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
    if (typeof entityID !== "undefined") {
      resolveStocks(
        entityID,
        filters.selected,
        status.active,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order
      )
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
