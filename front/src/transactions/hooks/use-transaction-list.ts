import { useEffect } from "react"

import { EntityType, Lots, TransactionQuery } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"
import { YearSelection } from "transactions/hooks/query/use-year"

import * as api from "../api"
import useAPI from "common/hooks/use-api"

function snapshotGetter(entity: EntitySelection) {
  switch (entity?.entity_type) {
    case EntityType.Administration:
      return api.getAdminSnapshot
    case EntityType.Auditor:
      return api.getAuditorSnapshot
    default:
      return api.getSnapshot
  }
}

// fetches current snapshot when parameters change
export function useGetSnapshot(entity: EntitySelection, year: YearSelection) {
  const [snapshot, resolveSnapshot] = useAPI(snapshotGetter(entity))

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

function lotsGetter(entity: EntitySelection) {
  switch (entity?.entity_type) {
    case EntityType.Administration:
      return api.getAdminLots
    case EntityType.Auditor:
      return api.getAuditorLots
    default:
      return api.getLots
  }
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
  filters: TransactionQuery
): LotGetter {
  const [transactions, resolveLots] = useAPI(lotsGetter(entity))

  function exportAllTransactions() {
    if (entity === null) return

    switch (entity.entity_type) {
      case EntityType.Administration:
        return api.downloadAdminLots(filters)
      case EntityType.Auditor:
        return api.downloadAuditorLots(filters)
      default:
        return api.downloadLots(filters)
    }
  }

  function getTransactions() {
    if (filters.entity_id >= 0) {
      resolveLots(filters)
    }
  }

  useEffect(getTransactions, [resolveLots, filters])

  return { ...transactions, getTransactions, exportAllTransactions }
}
