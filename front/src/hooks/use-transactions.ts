import { useState, useEffect } from "react"

import { EntitySelection } from "./use-app"
import { SelectValue } from "../components/system/select"
import { LotStatus, Filters, Lots, Snapshot } from "../services/types"

import useAPI from "./helpers/use-api"
import { PageSelection, usePageSelection } from "./helpers/use-pagination"
import { getSnapshot, getLots } from "../services/lots"

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
          pagination.page,
          pagination.limit
        )
      )
    }
  }, [
    resolve,
    status.active,
    entity.selected,
    filters.selected,
    pagination.page,
    pagination.limit,
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
