import { EntitySelection } from "./helpers/use-entity"

import useAPI from "./helpers/use-api"
import useTransactionForm from "../hooks/helpers/use-transaction-form"

import useClose from "./helpers/use-close"
import { addLot } from "../services/lots"

export default function useTransactionAdd(
  entity: EntitySelection,
  refresh: () => void
) {
  const close = useClose("../")
  const [form, change] = useTransactionForm()
  const [request, resolve] = useAPI(addLot)

  async function submit() {
    if (entity === null) return

    const res = await resolve(entity.id, form)

    if (res) {
      refresh()
      close()
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
