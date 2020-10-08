import { useState, useEffect } from "react"

import { EntitySelection } from "./use-app"
import { SelectValue } from "../components/system/select"
import { LotStatus, Filters, Lots, Snapshot } from "../services/types"

import { PageSelection, usePageSelection } from "../components/system/pagination" // prettier-ignore
import useAPI, { ApiState } from "./helpers/use-api"

import {
  getSnapshot,
  getLots,
  deleteLots,
  duplicateLot,
  validateLots,
} from "../services/lots"
import confirm from "../components/system/confirm"

export type SearchSelection = {
  query: string
  setQuery: (s: string) => void
}

// manage search query
function useSearchSelection(): SearchSelection {
  const [query, setQuery] = useState('')
  return { query, setQuery }
}

export type StatusSelection = {
  active: LotStatus
  setActive: (s: LotStatus) => void
}

// manage currently selected transaction status
function useStatusSelection(): StatusSelection {
  const [active, setActive] = useState(LotStatus.Draft)
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
  selectMany: (e: React.ChangeEvent<HTMLInputElement>, ids: number[]) => void
  setSelected: React.Dispatch<React.SetStateAction<number[]>>
}

function useTransactionSelection(): TransactionSelection {
  const [selected, setSelected] = useState<number[]>([])

  function has(id: number) {
    return selected.includes(id)
  }

  function selectOne(id: number) {
    if (has(id)) {
      setSelected(selected.filter((sid) => sid !== id))
    } else {
      setSelected([...selected, id])
    }
  }

  function selectMany(e: React.ChangeEvent<HTMLInputElement>, ids: number[]) {
    if (e.target.checked) {
      setSelected(ids)
    } else {
      setSelected([])
    }
  }

  return { selected, has, selectOne, selectMany, setSelected }
}

// fetches current snapshot when parameters change
function useGetSnapshot(
  entity: EntitySelection
): [ApiState<Snapshot>, () => void] {
  const [snapshot, resolveSnapshot] = useAPI(getSnapshot)

  function resolve() {
    if (entity.selected?.id) {
      resolveSnapshot(entity.selected.id)
    }
  }

  useEffect(resolve, [resolveSnapshot, entity.selected])

  return [snapshot, resolve]
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  pagination: PageSelection,
  selection: TransactionSelection,
  search: SearchSelection
): [ApiState<Lots>, () => void] {
  const [transactions, resolveLots] = useAPI(getLots)

  const { page, limit, setPage } = pagination
  const { setSelected } = selection

  function resolve() {
    if (entity.selected?.id) {
      resolveLots(
        status.active,
        entity.selected.id,
        filters.selected,
        page,
        limit,
        search.query,
      )
    }
  }

  useEffect(resolve, [
    resolveLots,
    status.active,
    entity.selected,
    filters.selected,
    page,
    limit,
    search.query,
  ])

  // reset page to 0 when filters change
  useEffect(() => {
    setPage(0)
    setSelected([])
  }, [
    status.active,
    entity.selected,
    filters.selected,
    limit,
    setPage,
    setSelected,
  ])

  return [transactions, resolve]
}

function useDuplicateLot(entity: EntitySelection, refresh: () => void) {
  const [request, resolveDuplicate] = useAPI(duplicateLot)

  async function resolve(lotID: number) {
    const shouldDuplicate = await confirm(
      "Dupliquer lots",
      "Voulez vous dupliquer ce lot ?"
    )

    if (entity.selected && shouldDuplicate) {
      resolveDuplicate(entity.selected.id, lotID).then(refresh)
    }
  }

  return { ...request, resolve }
}

function useDeleteLots(entity: EntitySelection, refresh: () => void) {
  const [request, resolveDelete] = useAPI(deleteLots)

  async function resolve(lotIDs: number[]) {
    const shouldDelete = await confirm(
      "Supprimer lots",
      "Voulez vous supprimer ce(s) lot(s) ?"
    )

    if (entity.selected && shouldDelete) {
      resolveDelete(entity.selected.id, lotIDs).then(refresh)
    }
  }

  return { ...request, resolve }
}

function useValidateLots(entity: EntitySelection, refresh: () => void) {
  const [request, resolveValidate] = useAPI(validateLots)

  async function resolve(lotIDs: number[]) {
    const shouldValidate = await confirm(
      "Envoyer lots",
      "Voulez vous envoyer ce(s) lot(s) ?"
    )

    if (entity.selected && shouldValidate) {
      resolveValidate(entity.selected.id, lotIDs).then(refresh)
    }
  }

  return { ...request, resolve }
}

export default function useTransactions(entity: EntitySelection) {
  const status = useStatusSelection()
  const filters = useFilterSelection()
  const pagination = usePageSelection()
  const selection = useTransactionSelection()
  const search = useSearchSelection()

  const [snapshot, resolveGetSnapshot] = useGetSnapshot(entity)
  const [transactions, resolveGetLots] = useGetLots(entity, status, filters, pagination, selection, search) // prettier-ignore

  function refresh() {
    resolveGetLots()
    resolveGetSnapshot()
  }

  const deleter = useDeleteLots(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const validator = useValidateLots(entity, refresh)

  return {
    status,
    filters,
    pagination,
    snapshot,
    transactions,
    selection,
    deleter,
    duplicator,
    validator,
    refresh,
    search,
  }
}
