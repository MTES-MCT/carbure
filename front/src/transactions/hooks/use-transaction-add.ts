import { EntitySelection } from "../../common/hooks/helpers/use-entity"

import useTransactionForm, {
  toTransactionPostData,
} from "../../common/hooks/helpers/use-transaction-form"

import { useRelativePush } from "../../common/components/relative-route"
import useAPI from "../../common/hooks/helpers/use-api"
import useClose from "../../common/hooks/helpers/use-close"
import { addLot } from "../api"
import { useNotificationContext } from "../../common/system/notifications"

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
