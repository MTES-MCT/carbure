import { useEffect } from "react"

import { EntityType, Lots } from "common/types"
import { PageSelection } from "common/components/pagination"
import { EntitySelection } from "carbure/hooks/use-entity"
import { FilterSelection } from "transactions/hooks/query/use-filters"
import { SearchSelection } from "transactions/hooks/query/use-search"
import { SortingSelection } from "transactions/hooks/query/use-sort-by"
import { StatusSelection } from "transactions/hooks/query/use-status"
import { YearSelection } from "transactions/hooks/query/use-year"
import { SpecialSelection } from "transactions/hooks/query/use-special"

import * as api from "../api"
import useAPI from "common/hooks/use-api"

// fetches current snapshot when parameters change
export function useGetSnapshot(entity: EntitySelection, year: YearSelection) {
  const snapshotGetter =
    entity?.entity_type === EntityType.Administration
      ? api.getAdminSnapshot
      : api.getSnapshot

  const [snapshot, resolveSnapshot] = useAPI(snapshotGetter)

  const entityID = entity?.id
  const years = snapshot.data?.years

  // if the currently selected year is not in the list of available years
  // set it to the first available value
  if (
    years?.length &&
    !years.some((option) => option.value === year.selected)
  ) {
    year.setYear(years[0].value as number)
  }

  function getSnapshot() {
    if (typeof entityID !== "undefined") {
      resolveSnapshot(entityID, year.selected)
    }
  }

  useEffect(getSnapshot, [resolveSnapshot, entityID, year.selected])

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
export function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  year: YearSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection,
  special: SpecialSelection
): LotGetter {
  const lotsGetter =
    entity?.entity_type === EntityType.Administration
      ? api.getAdminLots
      : api.getLots

  const [transactions, resolveLots] = useAPI(lotsGetter)

  const entityID = entity?.id

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
    if (typeof entityID !== "undefined") {
      resolveLots(
        status.active,
        entityID,
        filters.selected,
        year.selected,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order,
        special.invalid,
        special.deadline
      )
    }
  }

  useEffect(getTransactions, [
    resolveLots,
    status.active,
    entityID,
    filters.selected,
    year.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
    special.invalid,
    special.deadline,
  ])

  return { ...transactions, getTransactions, exportAllTransactions }
}
