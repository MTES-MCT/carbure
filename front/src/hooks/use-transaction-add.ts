import { EntitySelection } from "./helpers/use-entity"

import useTransactionForm, {
  toTransactionPostData,
} from "../hooks/helpers/use-transaction-form"

import { useRelativePush } from "../components/relative-route"
import useAPI from "./helpers/use-api"
import useClose from "./helpers/use-close"
import { addLot } from "../services/lots"
import { useNotificationContext } from "../components/system/notifications"

export default function useTransactionAdd(
  entity: EntitySelection,
  refresh: () => void
) {
  const notifications = useNotificationContext()

  const close = useClose("../")
  const relativePush = useRelativePush()
  const [form, hasChange, change] = useTransactionForm(entity)
  const [request, resolveAddLot] = useAPI(addLot)

  async function submit() {
    if (entity === null) return

    const res = await resolveAddLot(entity.id, toTransactionPostData(form))

    if (res) {
      refresh()
      relativePush(`../${res.id}`)

      notifications.push({
        level: "success",
        text: "Le lot a bien été créée !",
      })
    } else {
      notifications.push({
        level: "error",
        text: "Impossible de créer ce lot.",
      })
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
