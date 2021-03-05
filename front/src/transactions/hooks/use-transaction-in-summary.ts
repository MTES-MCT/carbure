import { useEffect } from "react"
import { EntitySelection } from "carbure/hooks/use-entity"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import { getLotsInSummary } from "../api"
import { LotStatus } from "common/types"

export interface TransactionInSummaryFormState {
  [vendor: string]: {
    [delivery_site: string]: {
      [biocarburant: string]: {
        volume: number
        avg_ghg_reduction: number
      }
    }
  }
}

export default function useTransactionInSummary(entity: EntitySelection, lot_status: LotStatus, period: string, delivery_status: string) {
  const close = useClose("..")
  const [request, resolve] = useAPI(getLotsInSummary)

  useEffect(() => {
    if (entity !== null) {
      resolve(entity.id, lot_status, period, delivery_status)
    }
  }, [resolve, entity])

  return {
    request,
    close,
  }
}
