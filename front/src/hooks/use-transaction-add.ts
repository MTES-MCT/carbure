import { EntitySelection } from "./use-app"

import useTransactionForm from "../hooks/helpers/use-transaction-form"

import useClose from "./helpers/use-close"
import { addLots } from "../services/lots"

export default function useTransactionAdd(entity: EntitySelection) {
  const close = useClose("/transactions")
  const { form, request, change, resolve } = useTransactionForm()

  function submit() {
    if (entity.selected && form) {
      resolve(addLots(entity.selected.id, form).then(close))
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
