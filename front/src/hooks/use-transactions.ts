import { useState, useEffect } from "react"

import { EntitySelection } from "./use-app"
import { SelectValue } from "../components/system/select"
import { LotStatus, Filters, Lots, Snapshot } from "../services/types"

import {
  PageSelection,
  usePageSelection,
} from "../components/system/pagination"
import useAPI, { ApiState } from "./helpers/use-api"

import {
  getSnapshot,
  getLots,
  deleteLots,
  duplicateLot,
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

// fetches current snapshot when parameters change
function useGetSnapshot(
  entity: EntitySelection
): [ApiState<Snapshot>, () => void] {
  const [snapshot, resolve] = useAPI<Snapshot>()

  function refresh() {
    if (entity.selected?.id) {
      resolve(getSnapshot(entity.selected.id))
    }
  }

  useEffect(refresh, [resolve, entity.selected])

  return [snapshot, refresh]
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  pagination: PageSelection
): [ApiState<Lots>, () => void] {
  const [transactions, resolve] = useAPI<Lots>()

  function resolveGetLots() {
    if (entity.selected?.id) {
      resolve(
        getLots(
          status.active,
          entity.selected.id,
          filters.selected,
          pagination.page,
          pagination.limit
        )
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
  const [request, resolve] = useAPI<void>()

  function resolveDuplicateLot(lotID: number) {
    if (entity.selected && window.confirm("Voulez vous dupliquer ce lot ?")) {
      resolve(duplicateLot(entity.selected.id, lotID).then(refresh))
    }
  }

  return { ...request, resolveDuplicateLot }
}

function useDeleteLots(entity: EntitySelection, refresh: () => void) {
  const [request, resolve] = useAPI<void>()

  function resolveDeleteLot(lotID: number) {
    if (entity.selected && window.confirm("Voulez vous supprimer ce lot ?")) {
      resolve(deleteLots(entity.selected.id, [lotID]).then(refresh))
    }
  }

  return { ...request, resolveDeleteLot }
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

  const deleter = useDeleteLots(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)

  return {
    status,
    filters,
    pagination,
    snapshot,
    transactions,
    deleter,
    duplicator,
    refresh,
  }
}
