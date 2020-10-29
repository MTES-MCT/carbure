import { useEffect } from "react"
import { Lots } from "../services/types"
import useAPI from "./helpers/use-api"
import { getStocks, getStockSnapshot } from "../services/lots"
import { EntitySelection } from "./helpers/use-entity"
import {
  PageSelection,
  usePageSelection,
} from "../components/system/pagination"
import useFilterSelection, { FilterSelection } from "./query/use-filters"
import useSearchSelection, { SearchSelection } from "./query/use-search"
import useSortingSelection, { SortingSelection } from "./query/use-sort-by"

interface StockHook {
  loading: boolean
  error: string | null
  data: Lots | null
  resolve: () => void
}

function useGetStockSnapshot(entity: EntitySelection) {
  const [snapshot, resolveStockSnapshot] = useAPI(getStockSnapshot)

  function resolve() {
    if (entity !== null) {
      return resolveStockSnapshot(entity.id).cancel
    }
  }

  useEffect(resolve, [resolveStockSnapshot, entity])

  return { ...snapshot, resolve }
}

// fetches current transaction list when parameters change
function useGetStocks(
  entity: EntitySelection,
  filters: FilterSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection
): StockHook {
  const [transactions, resolveStocks] = useAPI(getStocks)

  function resolve() {
    if (entity !== null) {
      return resolveStocks(
        entity.id,
        filters.selected,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order
      ).cancel
    }
  }

  useEffect(resolve, [
    resolveStocks,
    entity,
    filters.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
  ])

  return { ...transactions, resolve }
}

export function useStocks(entity: EntitySelection) {
  const pagination = usePageSelection()
  const sorting = useSortingSelection(pagination)

  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const transactions = useGetStocks(entity, filters, pagination, search, sorting) // prettier-ignore

  function refresh() {
    transactions.resolve()
  }

  return {
    filters,
    pagination,
    snapshot,
    transactions,
    search,
    sorting,
    refresh,
  }
}
