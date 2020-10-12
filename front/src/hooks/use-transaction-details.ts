import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { Lots } from "../services/types"
import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, {
  toTransactionFormState,
} from "./helpers/use-transaction-form"
import useAPI, { ApiState } from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { updateLot } from "../services/lots"

export default function useTransactionDetails(
  entity: EntitySelection,
  transactions: ApiState<Lots | null>,
  refresh: () => void
) {
  const close = useClose("../")
  const params: { id: string } = useParams()
  const [form, change, setForm] = useTransactionForm()
  const [request, resolve] = useAPI(updateLot)

  const transactionID = parseInt(params.id, 10)

  useEffect(() => {
    if (transactions) {
      // find the relevant lot
      // @TODO would be nice to be able to fetch details for only one lot
      const transaction = transactions.data?.lots.find(
        (lot) => lot.id === transactionID
      )

      // initialize the form with data coming from the loaded transaction
      if (transaction) {
        setForm(toTransactionFormState(transaction))
      }
    }
  }, [transactionID, transactions, setForm])

  function submit() {
    if (entity !== null && form) {
      resolve(entity, transactionID, form).then(close).then(refresh)
    }
  }

  return { form, request, change, submit, close }
}
