import { EntitySelection } from "./use-app"

import useAPI from "./helpers/use-api"
import useTransactionForm from "../hooks/helpers/use-transaction-form"

import useClose from "./helpers/use-close"
import { addLot } from "../services/lots"

export default function useTransactionAdd(entity: EntitySelection) {
  const close = useClose("/transactions")
  const [form, change] = useTransactionForm()
  const [request, resolve] = useAPI(addLot)

  function submit() {
    if (entity.selected && form) {
      resolve(entity.selected.id, form).then(close)
    }
  }

  return {
    form,
    request,
    change,
    submit,
    close,
  }
}
