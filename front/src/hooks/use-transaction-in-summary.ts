import { useEffect } from "react"
import { EntitySelection } from "./helpers/use-entity"

import useAPI from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { getLotsInSummary } from "../services/lots"

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

export default function useTransactionInSummary(entity: EntitySelection) {
  const close = useClose("..")
  const [request, resolve] = useAPI(getLotsInSummary)

  useEffect(() => {
    if (entity !== null) {
      resolve(entity.id)
    }
  }, [resolve, entity])

  return {
    request,
    close,
  }
}
