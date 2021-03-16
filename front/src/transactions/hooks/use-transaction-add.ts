import { EntitySelection } from "carbure/hooks/use-entity"

import useTransactionForm, {
  toTransactionPostData,
} from "transactions/hooks/use-transaction-form"

import { useRelativePush } from "common/components/relative-route"
import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import { addLot } from "../api"
import { useNotificationContext } from "common/components/notifications"

export default function useTransactionAdd(
  entity: EntitySelection,
  refresh: () => void
) {
  const notifications = useNotificationContext()

  const close = useClose("../")
  const relativePush = useRelativePush()
  const { data, hasChange, onChange } = useTransactionForm(entity)
  const [request, resolveAddLot] = useAPI(addLot)

  async function submit() {
    if (entity === null) return

    const res = await resolveAddLot(entity.id, toTransactionPostData(data))

    if (res) {
      refresh()
      relativePush(`../${res.id}`)

      notifications.push({
        level: "success",
        text: "Le lot a bien été créé !",
      })
    } else {
      notifications.push({
        level: "error",
        text: "Impossible de créer ce lot.",
      })
    }
  }

  return {
    form: data,
    hasChange,
    request,
    change: onChange,
    submit,
    close,
  }
}
