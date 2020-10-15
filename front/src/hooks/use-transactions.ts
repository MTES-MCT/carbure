import { useState, useEffect } from "react"

import { SelectValue } from "../components/system/select"
import { LotStatus, Filters } from "../services/types"

import { PageSelection, usePageSelection } from "../components/system/pagination" // prettier-ignore
import useAPI from "./helpers/use-api"

import {
  getSnapshot,
  getLots,
  downloadLots,
  deleteLots,
  duplicateLot,
  validateLots,
  validateAllDraftLots,
  deleteAllDraftLots,
  uploadLotFile,
} from "../services/lots"

import confirm from "../components/system/confirm"
import { useHistory, useParams } from "react-router-dom"
import useEntity, { EntitySelection } from "./helpers/use-entity"

export type SearchSelection = {
  query: string
  setQuery: (s: string) => void
}

// manage search query
function useSearchSelection(): SearchSelection {
  const [query, setQuery] = useState("")
  return { query, setQuery }
}

export type StatusSelection = {
  active: LotStatus
  setActive: (s: LotStatus) => void
}

// manage currently selected transaction status
function useStatusSelection(): StatusSelection {
  const history = useHistory()
  const params: { status: LotStatus } = useParams()

  const active = params.status
  const setActive = (status: LotStatus) => history.push(`/org/${status}`)

  return { active, setActive }
}

export type FilterSelection = {
  selected: { [k in Filters]: SelectValue }
  selectFilter: (type: Filters, value: SelectValue) => void
}

// manage current filter selection
function useFilterSelection(): FilterSelection {
  const [selected, setFilters] = useState({
    [Filters.Biocarburants]: null,
    [Filters.MatieresPremieres]: null,
    [Filters.CountriesOfOrigin]: null,
    [Filters.Periods]: null,
    [Filters.Clients]: null,
    [Filters.ProductionSites]: null,
    [Filters.Year]: new Date().getFullYear(),
  })

  function selectFilter(type: Filters, value: SelectValue) {
    setFilters({ ...selected, [type]: value })
  }

  return { selected, selectFilter }
}

export type TransactionSelection = {
  selected: number[]
  has: (id: number) => boolean
  selectOne: (id: number) => void
  selectMany: React.Dispatch<React.SetStateAction<number[]>>
  reset: () => void
}

function useTransactionSelection(): TransactionSelection {
  const [selected, selectMany] = useState<number[]>([])

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

export type SortingSelection = {
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
function useGetSnapshot(entity: EntitySelection, year: number | null) {
  const [snapshot, resolveSnapshot] = useAPI(getSnapshot)

  function resolve() {
    if (entity !== null && year !== null) {
      return resolveSnapshot(entity, year).cancel
    }
  }

  useEffect(resolve, [resolveSnapshot, entity, year])

  return { ...snapshot, resolve }
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  pagination: PageSelection,
  selection: TransactionSelection,
  search: SearchSelection,
  sorting: SortingSelection
) {
  const [transactions, resolveLots] = useAPI(getLots)

  const { page, limit, setPage } = pagination
  const { selectMany } = selection

  function resolve() {
    if (entity !== null) {
      return resolveLots(
        status.active,
        entity,
        filters.selected,
        page,
        limit,
        search.query,
        sorting.column,
        sorting.order
      ).cancel
    }
  }

  function exportAll() {
    if (entity !== null) {
      downloadLots(
        status.active,
        entity,
        filters.selected,
        search.query,
        sorting.column,
        sorting.order
      )
    }
  }

  // reset page to 0 when filters change
  useEffect(() => {
    setPage(0)
    selectMany([])
  }, [
    status.active,
    entity,
    filters.selected,
    sorting.column,
    sorting.order,
    limit,
    setPage,
    selectMany,
  ])

  useEffect(resolve, [
    resolveLots,
    status.active,
    entity,
    filters.selected,
    page,
    limit,
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
      resolveDelete(entity, [lotID]).then(selection.reset).then(refresh)
    }
  }

  async function resolveSelection() {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer les lots sélectionnés ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDelete(entity, selection.selected)
        .then(selection.reset)
        .then(refresh)
    }
  }

  async function resolveAll() {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer tous ces lots ?"
    )

    if (entity !== null && shouldDelete) {
      resolveDeleteAll(entity).then(refresh)
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
      resolveValidate(entity, [lotID]).then(selection.reset).then(refresh)
    }
  }

  async function resolveSelection() {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer les lots sélectionnés ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidate(entity, selection.selected)
        .then(selection.reset)
        .then(refresh)
    }
  }

  async function resolveAll() {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer tous ces lots ?"
    )

    if (entity !== null && shouldValidate) {
      resolveValidateAll(entity).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    resolve,
    resolveSelection,
    resolveAll,
  }
}

export default function useTransactions() {
  const entity = useEntity()

  const status = useStatusSelection()
  const filters = useFilterSelection()
  const pagination = usePageSelection()
  const selection = useTransactionSelection()
  const search = useSearchSelection()
  const sorting = useSortingSelection()

  const snapshot = useGetSnapshot(entity, filters.selected[Filters.Year] as number | null) // prettier-ignore
  const transactions = useGetLots(entity, status, filters, pagination, selection, search, sorting) // prettier-ignore

  function refresh() {
    snapshot.resolve()
    transactions.resolve()
  }

  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, refresh)
  const validator = useValidateLots(entity, selection, refresh)

  return {
    entity,
    status,
    filters,
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
