import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, {
  toTransactionPostData,
} from "../hooks/helpers/use-transaction-form"

import useAPI from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { addLot } from "../services/lots"

export default function useTransactionAdd(
  entity: EntitySelection,
  refresh: () => void
) {
  const close = useClose("../")
  const [form, hasChange, change] = useTransactionForm(entity)
  const [request, resolve] = useAPI(addLot)

  async function submit() {
    if (entity === null) return

    const res = await resolve(entity.id, toTransactionPostData(form))

    if (res) {
      refresh()
      close()
    }
  }

  return {
    form,
    hasChange,
    request,
    change,
    submit,
    close,
  }
}
