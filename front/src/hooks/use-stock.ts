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
import { useStockStatusSelection, StatusSelection } from "./query/use-status"
import useInvalidSelection from "./query/use-invalid"
import useDeadlineSelection from "./query/use-deadline"

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
  status: StatusSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection
): StockHook {
  const [stock, resolveStocks] = useAPI(getStocks)
  const entityID = entity?.id

  function resolve() {
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

  useEffect(resolve, [
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

  return { ...stock, resolve }
}

export function useStocks(entity: EntitySelection) {
  const pagination = usePageSelection()
  const sorting = useSortingSelection(pagination)
  const status = useStockStatusSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const stock = useGetStocks(entity, filters, status, pagination, search, sorting) // prettier-ignore

  return {
    filters,
    pagination,
    snapshot,
    status,
    stock,
    search,
    sorting,
  }
}
