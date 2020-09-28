import { useState, useEffect } from "react"

import { EntitySelection } from "./use-app"
import { SelectValue } from "../components/dropdown/select"
import { LotStatus, Filters, Lots, Snapshot } from "../services/types"

import useAPI from "../hooks/use-api"
import { getSnapshot, getLots } from "../services/lots"

// @TODO harcoded pagination limit value
const LIMIT = 10

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

export type PageSelection = {
  selected: {
    page: number
    limit: number
  }

  setPage: (p: number) => void
  setLimit: (l: number) => void
}

// manage pagination state
function usePageSelection(): PageSelection {
  const [selected, setPagination] = useState({ page: 0, limit: LIMIT })

  function setPage(page: number) {
    setPagination({ ...selected, page })
  }

  function setLimit(limit: number) {
    setPagination({ ...selected, limit })
  }

  return { selected, setPage, setLimit }
}

// fetches current snapshot when parameters change
function useGetSnapshot(entity: EntitySelection) {
  const [snapshot, resolve] = useAPI<Snapshot>()

  useEffect(() => {
    if (entity.selected?.id) {
      resolve(getSnapshot(entity.selected.id))
    }
  }, [resolve, entity.selected])

  return snapshot
}

// fetches current transaction list when parameters change
function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  pagination: PageSelection
) {
  const [transactions, resolve] = useAPI<Lots>()

  useEffect(() => {
    if (entity.selected?.id) {
      resolve(
        getLots(
          status.active,
          entity.selected.id,
          filters.selected,
          pagination.selected
        )
      )
    }
  }, [
    resolve,
    status.active,
    entity.selected,
    filters.selected,
    pagination.selected,
  ])

  return transactions
}

export default function useTransactions(entity: EntitySelection) {
  const status = useStatusSelection()
  const filters = useFilterSelection()
  const pagination = usePageSelection()

  const snapshot = useGetSnapshot(entity)
  const transactions = useGetLots(entity, status, filters, pagination)

  return { status, filters, pagination, snapshot, transactions }
}
