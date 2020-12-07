import { useEffect } from "react"
import { EntitySelection } from "../../common/hooks/helpers/use-entity"
import useAPI from "../../common/hooks/helpers/use-api"
import useClose from "../../common/hooks/helpers/use-close"
import { getLotsOutSummary } from "../api"

export interface TransactionOutSummaryFormState {
  [client: string]: {
    [delivery_site: string]: {
      [biocarburant: string]: {
        volume: number
        avg_ghg_reduction: number
      }
    }
  }
}

export default function useTransactionOutSummary(entity: EntitySelection) {
  const close = useClose("..")
  const [request, resolve] = useAPI(getLotsOutSummary)

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
