import { useEffect } from "react"

import { Lots } from "../services/types"
import { PageSelection } from "../components/system/pagination"
import { EntitySelection } from "./helpers/use-entity"
import { FilterSelection } from "./query/use-filters"
import { SearchSelection } from "./query/use-search"
import { SortingSelection } from "./query/use-sort-by"
import { StatusSelection } from "./query/use-status"
import { YearSelection } from "./query/use-year"
import { InvalidSelection } from "./query/use-invalid"
import { DeadlineSelection } from "./query/use-deadline"

import * as api from "../services/lots"
import useAPI from "./helpers/use-api"

import { usePageSelection } from "../components/system/pagination" // prettier-ignore

import useUploadLotFile from "./actions/use-upload-file"
import useDuplicateLot from "./actions/use-duplicate-lots"
import useDeleteLots from "./actions/use-delete-lots"
import useValidateLots from "./actions/use-validate-lots"
import useRejectLots from "./actions/use-reject-lots"
import useAcceptLots from "./actions/use-accept-lots"

import useFilterSelection from "./query/use-filters"
import useSearchSelection from "./query/use-search"
import useTransactionSelection from "./query/use-selection"
import useSortingSelection from "./query/use-sort-by"
import useStatusSelection from "./query/use-status"
import useYearSelection from "./query/use-year"
import useInvalidSelection from "./query/use-invalid"
import useDeadlineSelection from "./query/use-deadline"

// fetches current snapshot when parameters change
function useGetSnapshot(entity: EntitySelection, year: YearSelection) {
  const [snapshot, resolveSnapshot] = useAPI(api.getSnapshot)

  const years = snapshot.data?.years

  // if the currently selected year is not in the list of available years
  // set it to the first available value
  if (years && !years.some((option) => option.value === year.selected)) {
    year.setYear(years[0].value as number)
  }

  function getSnapshot() {
    if (entity !== null) {
      return resolveSnapshot(entity.id, year.selected).cancel
    }
  }

  useEffect(getSnapshot, [resolveSnapshot, entity, year.selected])

  return { ...snapshot, getSnapshot }
}

export interface LotGetter {
  loading: boolean
  error: string | null
  data: Lots | null
  getTransactions: () => void
  exportAllTransactions: () => void
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  year: YearSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection,
  invalid: InvalidSelection,
  deadline: DeadlineSelection
): LotGetter {
  const [transactions, resolveLots] = useAPI(api.getLots)

  function exportAllTransactions() {
    if (entity !== null) {
      api.downloadLots(
        status.active,
        entity.id,
        filters.selected,
        year.selected,
        search.query,
        sorting.column,
        sorting.order
      )
    }
  }

  function getTransactions() {
    if (entity !== null) {
      return resolveLots(
        status.active,
        entity.id,
        filters.selected,
        year.selected,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order,
        invalid.active,
        deadline.active
      ).cancel
    }
  }

  useEffect(getTransactions, [
    resolveLots,
    status.active,
    entity?.id,
    filters.selected,
    year.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
    invalid.active,
    deadline.active,
  ])

  return { ...transactions, getTransactions, exportAllTransactions }
}

export default function useTransactions(entity: EntitySelection) {
  const pagination = usePageSelection()

  const invalid = useInvalidSelection(pagination)
  const deadline = useDeadlineSelection(pagination)
  const sorting = useSortingSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const status = useStatusSelection(pagination, invalid, deadline)
  const year = useYearSelection(pagination, filters, invalid, deadline)

  const snapshot = useGetSnapshot(entity, year)
  const transactions = useGetLots(entity, status, filters, year, pagination, search, sorting, invalid, deadline) // prettier-ignore

  function refresh() {
    snapshot.getSnapshot()
    transactions.getTransactions()
  }

  const selection = useTransactionSelection(transactions.data?.lots)

  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, year, refresh)
  const validator = useValidateLots(entity, selection, year, refresh)
  const acceptor = useAcceptLots(entity, selection, year, refresh)
  const rejector = useRejectLots(entity, selection, year, refresh)

  return {
    entity,
    status,
    filters,
    year,
    pagination,
    snapshot,
    transactions,
    selection,
    search,
    invalid,
    deadline,
    sorting,
    deleter,
    uploader,
    duplicator,
    validator,
    acceptor,
    rejector,
    refresh,
  }
}
