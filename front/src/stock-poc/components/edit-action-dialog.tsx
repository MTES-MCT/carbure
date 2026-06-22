import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { updateAction } from "../api"
import { Action } from "../types"
import { actionToFormValue } from "../utils"
import { ActionForm, ActionFormValue } from "./action-form"
import { INVALIDATES, toActionRequestBody } from "./create-action-dialog"

export const EditActionDialog = ({
  entityId,
  action,
  actions,
  onClose,
}: {
  entityId: number
  action: Action
  actions: Action[]
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const mutation = useMutation(
    (entity_id: number, body: ReturnType<typeof toActionRequestBody>) =>
      updateAction(entity_id, action.id, body),
    {
      invalidates: INVALIDATES,
      onSuccess: () => {
        notify(t("Action modifiée."), { variant: "success" })
      },
      onError: () => {
        notify(t("La modification de l'action a échoué."), {
          variant: "danger",
        })
      },
    }
  )

  return (
    <Dialog
      header={
        <Dialog.Title>
          {t("Modifier l'action #{{id}}", { id: action.id })}
        </Dialog.Title>
      }
      footer={
        <Button
          type="submit"
          loading={mutation.loading}
          nativeButtonProps={{ form: "stock-poc-action-edit-form" }}
        >
          {t("Enregistrer")}
        </Button>
      }
      onClose={onClose}
    >
      <ActionForm
        key={action.id}
        formId="stock-poc-action-edit-form"
        actions={actions}
        excludeActionId={action.id}
        initialValue={actionToFormValue(action)}
        onSubmit={(value: ActionFormValue) => {
          if (!value.type || value.quantity === undefined) return
          mutation.execute(entityId, toActionRequestBody(value)).then(onClose)
        }}
      />
    </Dialog>
  )
}
