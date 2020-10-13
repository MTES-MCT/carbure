import { useEffect } from "react"
import { EntitySelection } from "./helpers/use-entity"

import useAPI from "./helpers/use-api"
import useForm from "../hooks/helpers/use-form"

import useClose from "./helpers/use-close"
import { getLotsOutSummary } from "../services/lots"

export interface TransactionOutSummaryFormState {
  [delivery_site: string]: {
    [supplier: string]: {
      [biocarburant: string]: {
        volume: number
        avg_ghg_reduction: number
      }
    }
  }
}

export default function useTransactionOutSummary(entity: EntitySelection) {
  const close = useClose("..")
  const [form, change] = useForm({})
  const [request, resolve] = useAPI(getLotsOutSummary)

  useEffect(() => {
    if (entity !== null) {
      resolve(entity)
    }
  }, [resolve, entity])

  return {
    form,
    request,
    change,
    close,
  }
}
