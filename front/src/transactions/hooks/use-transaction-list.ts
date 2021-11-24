import { useEffect } from "react"

import { EntityType, Lots, TransactionQuery } from "common/types"
import { Entity } from "carbure/types"
import { YearSelection } from "transactions/hooks/query/use-year"

import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { useTranslation } from "react-i18next"

function snapshotGetter(entity: Entity) {
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
export function useGetSnapshot(entity: Entity, year: YearSelection) {
  const { t } = useTranslation()
  const [snapshot, resolveSnapshot] = useAPI(snapshotGetter(entity))

  const entityID = entity?.id
  const checkYears = year.checkYears

  function getSnapshot() {
    if (typeof entityID !== "undefined") {
      resolveSnapshot(entityID, year.selected, t)
    }
  }

  useEffect(getSnapshot, [resolveSnapshot, entityID, year.selected, t])

  useEffect(() => {
    if (snapshot.data) {
      checkYears(snapshot.data.years)
    }
  }, [snapshot, checkYears])

  return { ...snapshot, getSnapshot }
}

function lotsGetter(entity: Entity) {
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
  entity: Entity,
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
