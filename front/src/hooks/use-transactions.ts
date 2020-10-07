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
  has: (id: number) => boolean
  selectOne: (id: number) => void
  selectAll: (e: React.ChangeEvent<HTMLInputElement>) => void
}

function useTransactionSelection(
  transactions: Lots | null
): TransactionSelection {
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

  function selectAll(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.checked && transactions) {
      setSelected(transactions.lots.map((tx) => tx.id))
    } else {
      setSelected([])
    }
  }

  return { has, selectOne, selectAll }
}

// fetches current snapshot when parameters change
function useGetSnapshot(
  entity: EntitySelection
): [ApiState<Snapshot>, () => void] {
  const [snapshot, resolve] = useAPI(getSnapshot)

  function resolveGetLots() {
    if (entity.selected?.id) {
      resolve(entity.selected.id)
    }
  }

  useEffect(resolveGetLots, [resolve, entity.selected])

  return [snapshot, resolveGetLots]
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  pagination: PageSelection
): [ApiState<Lots>, () => void] {
  const [transactions, resolve] = useAPI(getLots)

  function resolveGetLots() {
    if (entity.selected?.id) {
      resolve(
        status.active,
        entity.selected.id,
        filters.selected,
        pagination.page,
        pagination.limit
      )
    }
  }

  useEffect(resolveGetLots, [
    resolve,
    status.active,
    entity.selected,
    filters.selected,
    pagination.page,
    pagination.limit,
  ])

  return [transactions, resolveGetLots]
}

function useDuplicateLot(entity: EntitySelection, refresh: () => void) {
  const [request, resolveDuplicate] = useAPI(duplicateLot)

  function resolve(lotID: number) {
    if (entity.selected && window.confirm("Voulez vous dupliquer ce lot ?")) {
      resolveDuplicate(entity.selected.id, lotID).then(refresh)
    }
  }

  return { ...request, resolve }
}

function useDeleteLots(entity: EntitySelection, refresh: () => void) {
  const [request, resolveDelete] = useAPI(deleteLots)

  function resolve(lotID: number) {
    if (entity.selected && window.confirm("Voulez vous supprimer ce lot ?")) {
      resolveDelete(entity.selected.id, [lotID]).then(refresh)
    }
  }

  return { ...request, resolve }
}

function useValidateLots(entity: EntitySelection, refresh: () => void) {
  const [request, resolveValidate] = useAPI(validateLots)

  function resolve(lotID: number) {
    if (entity.selected && window.confirm("Voulez vous envoyer ce lot ?")) {
      resolveValidate(entity.selected.id, [lotID]).then(refresh)
    }
  }

  return { ...request, resolve }
}

export default function useTransactions(entity: EntitySelection) {
  const status = useStatusSelection()
  const filters = useFilterSelection()
  const pagination = usePageSelection()

  const [snapshot, resolveGetSnapshot] = useGetSnapshot(entity)
  const [transactions, resolveGetLots] = useGetLots(entity, status, filters, pagination) // prettier-ignore

  function refresh() {
    resolveGetLots()
    resolveGetSnapshot()
  }

  const selection = useTransactionSelection(transactions.data)

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
  }
}
