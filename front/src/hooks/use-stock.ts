import { useEffect } from "react"
import { Lots } from "../services/types"
import useAPI from "./helpers/use-api"
import { getStocks, getStockSnapshot } from "../services/stocks"
import { EntitySelection } from "./helpers/use-entity"
import useYearSelection from "./query/use-year"
import {
  PageSelection,
  usePageSelection,
} from "../components/system/pagination"
import useFilterSelection, { FilterSelection } from "./query/use-filters"
import useSearchSelection, { SearchSelection } from "./query/use-search"
import useSortingSelection, { SortingSelection } from "./query/use-sort-by"
import { useStockStatusSelection, StatusSelection } from "./query/use-status"
import useTransactionSelection from "./query/use-selection"

import useUploadLotFile from "./actions/use-upload-file"
import useDuplicateLot from "./actions/use-duplicate-lots"
import useDeleteLots from "./actions/use-delete-lots"
import useValidateLots from "./actions/use-validate-lots"
import useRejectLots from "./actions/use-reject-lots"
import useAcceptLots from "./actions/use-accept-lots"
import useSpecialSelection from "./query/use-special"
import useSendLot from "./actions/use-send-lots"

export interface StockHook {
  loading: boolean
  error: string | null
  data: Lots | null
  getStock: () => void
  exportAllTransactions: () => void
}

function useGetStockSnapshot(entity: EntitySelection) {
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

export function useStocks(entity: EntitySelection) {
  const pagination = usePageSelection()
  const sorting = useSortingSelection(pagination)
  const status = useStockStatusSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const special = useSpecialSelection(pagination)
  const year = useYearSelection(pagination, filters, special)
  const stock = useGetStocks(entity, filters, status, pagination, search, sorting) // prettier-ignore

  function refresh() {
    snapshot.getSnapshot()
    stock.getStock()
  }

  const selection = useTransactionSelection(stock.data?.lots)
  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, year, refresh)
  const validator = useValidateLots(entity, selection, year, refresh)
  const acceptor = useAcceptLots(entity, selection, year, refresh)
  const rejector = useRejectLots(entity, selection, year, refresh)
  const sender = useSendLot(entity, refresh)

  return {
    filters,
    pagination,
    snapshot,
    status,
    stock,
    search,
    sorting,
    selection,
    uploader,
    duplicator,
    deleter,
    validator,
    acceptor,
    rejector,
    sender,
  }
}
