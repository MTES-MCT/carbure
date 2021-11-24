import { useTranslation } from "react-i18next"
import { Entity } from "carbure/types"
import { useNavigate } from "react-router-dom"

import useTransactionForm, {
  toTransactionPostData,
} from "transactions/hooks/use-transaction-form"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import { addLot } from "../api"
import { useNotificationContext } from "common/components/notifications"

export default function useTransactionAdd(entity: Entity, refresh: () => void) {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const close = useClose("../")
  const relativePush = useNavigate()
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
        text: t("Le lot a bien été créé !"),
      })
    } else {
      notifications.push({
        level: "error",
        text: t("Impossible de créer ce lot."),
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
