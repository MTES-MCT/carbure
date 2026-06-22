import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { createAction } from "../api"
import { Action } from "../types"
import { ActionForm, ActionFormValue } from "./action-form"

export const INVALIDATES = ["stock-poc-tree"]

export function toActionRequestBody(value: ActionFormValue) {
  return {
    type: value.type!,
    status: value.status ?? null,
    quantity: String(value.quantity),
    parent: value.parent ?? null,
    owner: value.owner?.id,
  }
}

export const CreateActionDialog = ({
  entityId,
  actions,
  onClose,
}: {
  entityId: number
  actions: Action[]
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const mutation = useMutation(createAction, {
    invalidates: INVALIDATES,
    onSuccess: () => {
      notify(t("Action créée."), { variant: "success" })
    },
    onError: () => {
      notify(t("La création de l'action a échoué."), { variant: "danger" })
    },
  })

  return (
    <Dialog
      header={<Dialog.Title>{t("Créer une action")}</Dialog.Title>}
      footer={
        <Button
          type="submit"
          loading={mutation.loading}
          nativeButtonProps={{ form: "stock-poc-action-create-form" }}
        >
          {t("Créer l'action")}
        </Button>
      }
      onClose={onClose}
    >
      <ActionForm
        formId="stock-poc-action-create-form"
        actions={actions}
        onSubmit={(value) => {
          if (!value.type || value.quantity === undefined) return
          mutation.execute(entityId, toActionRequestBody(value)).then(onClose)
        }}
      />
    </Dialog>
  )
}
