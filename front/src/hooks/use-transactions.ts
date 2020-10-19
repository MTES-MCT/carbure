import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"

import { SelectValue } from "../components/system/select"
import { LotStatus, Filters, Lots } from "../services/types"

import { PageSelection, usePageSelection } from "../components/system/pagination" // prettier-ignore
import useAPI from "./helpers/use-api"

import {
  getSnapshot,
  getLots,
  getStocks,
  getStockSnapshot,
  downloadLots,
  deleteLots,
  duplicateLot,
  validateLots,
  validateAllDraftLots,
  deleteAllDraftLots,
  uploadLotFile,
} from "../services/lots"

import confirm from "../components/system/confirm"
import useEntity, { EntitySelection } from "./helpers/use-entity"
import { useRelativePush } from "../components/relative-route"

export interface SearchSelection {
  query: string
  setQuery: (s: string) => void
}

// manage search query
function useSearchSelection(pagination: PageSelection): SearchSelection {
  const [query, setQueryState] = useState("")

  function setQuery(query: string) {
    pagination.setPage(0)
    setQueryState(query)
  }

  return { query, setQuery }
}

export interface StatusSelection {
  active: LotStatus
  setActive: (s: LotStatus) => void
}

// manage currently selected transaction status
function useStatusSelection(pagination: PageSelection): StatusSelection {
  const push = useRelativePush()
  const params: { status: LotStatus } = useParams()

  const active = params.status

  function setActive(status: LotStatus) {
    pagination.setPage(0)
    push(`../${status}`)
  }

  return { active, setActive }
}

export interface FilterSelection {
  selected: { [k in Filters]: SelectValue }
  select: (type: Filters, value: SelectValue) => void
  reset: () => void
}

// manage current filter selection
function useFilterSelection(pagination: PageSelection): FilterSelection {
  const [selected, setFilters] = useState<FilterSelection["selected"]>({
    [Filters.Biocarburants]: null,
    [Filters.MatieresPremieres]: null,
    [Filters.CountriesOfOrigin]: null,
    [Filters.Periods]: null,
    [Filters.Clients]: null,
    [Filters.ProductionSites]: null,
  })

  function select(type: Filters, value: SelectValue) {
    pagination.setPage(0)
    setFilters({ ...selected, [type]: value })
  }

  function reset() {
    setFilters({
      [Filters.Biocarburants]: null,
      [Filters.MatieresPremieres]: null,
      [Filters.CountriesOfOrigin]: null,
      [Filters.Periods]: null,
      [Filters.Clients]: null,
      [Filters.ProductionSites]: null,
    })
  }

  return { selected, select, reset }
}

export interface YearSelection {
  selected: number
  setYear: (y: number) => void
}

function useYearSelection(
  pagination: PageSelection,
  filters: FilterSelection
): YearSelection {
  const [selected, setSelected] = useState(new Date().getFullYear())

  function setYear(year: number) {
    pagination.setPage(0)
    filters.reset()
    setSelected(year)
  }

  return { selected, setYear }
}

export interface TransactionSelection {
  selected: number[]
  has: (id: number) => boolean
  selectOne: (id: number) => void
  selectMany: React.Dispatch<React.SetStateAction<number[]>>
  reset: () => void
}

function useTransactionSelection(
  transactions: TransactionHook
): TransactionSelection {
  const [selected, selectMany] = useState<number[]>([])

  const tx = transactions.data?.lots.map((lot) => lot.id) ?? []

  // if some selected transactions are not on the current list, remove them
  if (selected.some((id) => !tx.includes(id))) {
    selectMany(selected.filter((id) => tx.includes(id)))
  }

  function has(id: number) {
    return selected.includes(id)
  }

  function reset() {
    selectMany([])
  }

  function selectOne(id: number) {
    if (has(id)) {
      selectMany(selected.filter((sid) => sid !== id))
    } else {
      selectMany([...selected, id])
    }
  }

  return { selected, has, selectOne, selectMany, reset }
}

// valeurs acceptables pour le sort_by: ['period', 'client', 'biocarburant', 'matiere_premiere', 'ghg_reduction', 'volume', 'pays_origine']

export interface SortingSelection {
  column: string
  order: "asc" | "desc"
  sortBy: (c: string) => void
}

function useSortingSelection(): SortingSelection {
  const [current, setCurrent] = useState<{
    column: string
    order: "asc" | "desc"
  }>({ column: "", order: "asc" })

  function sortBy(column: string) {
    if (current.column !== column) {
      return setCurrent({ column, order: "asc" })
    } else if (current.column && current.order === "asc") {
      return setCurrent({ column, order: "desc" })
    } else if (current.column && current.order === "desc") {
      return setCurrent({ column: "", order: "asc" })
    }
  }

  return { ...current, sortBy }
}

// fetches current snapshot when parameters change
function useGetSnapshot(entity: EntitySelection, year: YearSelection) {
  const [snapshot, resolveSnapshot] = useAPI(getSnapshot)

  const years = snapshot.data?.years

  // if the currently selected year is not in the list of available years
  // set it to the first available value
  if (years && !years.some((option) => option.value === year.selected)) {
    year.setYear(years[0].value as number)
  }

  function resolve() {
    if (entity !== null) {
      return resolveSnapshot(entity, year.selected).cancel
    }
  }

  useEffect(resolve, [resolveSnapshot, entity, year.selected])

  return { ...snapshot, resolve }
}

interface TransactionHook {
  loading: boolean
  error: string | null
  data: Lots | null
  resolve: () => void
  exportAll: () => void
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  year: YearSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection
): TransactionHook {
  const [transactions, resolveLots] = useAPI(getLots)

  function exportAll() {
    if (entity !== null) {
      downloadLots(
        status.active,
        entity,
        filters.selected,
        year.selected,
        search.query,
        sorting.column,
        sorting.order
      )
    }
  }

  function resolve() {
    if (entity !== null) {
      return resolveLots(
        status.active,
        entity,
        filters.selected,
        year.selected,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order
      ).cancel
    }
  }

  useEffect(resolve, [
    resolveLots,
    status.active,
    entity,
    filters.selected,
    year.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
  ])

  return { ...transactions, resolve, exportAll }
}

export interface Uploader {
  loading: boolean
  data: any
  error: string | null
  resolve: (f: File) => void
}

function useUploadLotFile(
  entity: EntitySelection,
  refresh: () => void
): Uploader {
  const [request, resolveUpload] = useAPI(uploadLotFile)

  async function resolve(file: File) {
    if (entity !== null) {
      resolveUpload(entity, file).then(refresh)
    }
  }

  return { ...request, resolve }
}

function useDuplicateLot(entity: EntitySelection, refresh: () => void) {
  const [request, resolveDuplicate] = useAPI(duplicateLot)

  async function resolve(lotID: number) {
    const shouldDuplicate = await confirm(
      "Dupliquer lots",
      "Voulez vous dupliquer ce lot ?"
    )

    if (entity !== null && shouldDuplicate) {
      resolveDuplicate(entity, lotID).then(refresh)
    }
  }

  return { ...request, resolve }
}

export interface Deleter {
  loading: boolean
  resolve: (l: number) => void
  resolveSelection: () => void
  resolveAll: () => void
}

function useDeleteLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): Deleter {
  const [request, resolveDelete] = useAPI(deleteLots)
  const [requestAll, resolveDeleteAll] = useAPI(deleteAllDraftLots)

  async function resolve(lotID: number) {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer ce lot ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDelete(entity, [lotID]).then(refresh)
    }
  }

  async function resolveSelection() {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer les lots sélectionnés ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDelete(entity, selection.selected).then(refresh)
    }
  }

  async function resolveAll() {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer tous ces lots ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDeleteAll(entity, year.selected).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    resolve,
    resolveSelection,
    resolveAll,
  }
}

export interface Validator {
  loading: boolean
  resolve: (l: number) => void
  resolveSelection: () => void
  resolveAll: () => void
}

function useValidateLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): Validator {
  const [request, resolveValidate] = useAPI(validateLots)
  const [requestAll, resolveValidateAll] = useAPI(validateAllDraftLots)

  async function resolve(lotID: number) {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer ce lot ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidate(entity, [lotID]).then(refresh)
    }
  }

  async function resolveSelection() {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer les lots sélectionnés ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidate(entity, selection.selected).then(refresh)
    }
  }

  async function resolveAll() {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer tous ces lots ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidateAll(entity, year.selected).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    resolve,
    resolveSelection,
    resolveAll,
  }
}

export function useTransactions() {
  const entity = useEntity()

  const sorting = useSortingSelection()
  const pagination = usePageSelection()

  const status = useStatusSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const year = useYearSelection(pagination, filters)

  const snapshot = useGetSnapshot(entity, year)
  const transactions = useGetLots(entity, status, filters, year, pagination, search, sorting) // prettier-ignore

  function refresh() {
    snapshot.resolve()
    transactions.resolve()
  }

  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)

  const selection = useTransactionSelection(transactions)

  const deleter = useDeleteLots(entity, selection, year, refresh)
  const validator = useValidateLots(entity, selection, year, refresh)

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
    sorting,
    deleter,
    uploader,
    duplicator,
    validator,
    refresh,
  }
}

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
      return resolveStockSnapshot(entity, ).cancel
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
        entity,
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

export function useStocks() {
  const entity = useEntity()

  const sorting = useSortingSelection()
  const pagination = usePageSelection()

  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const transactions = useGetStocks(entity, filters, pagination, search, sorting) // prettier-ignore

  function refresh() {
    transactions.resolve()
  }

  return {
    entity,
    filters,
    pagination,
    snapshot,
    transactions,
    search,
    sorting,
    refresh,
  }
}
