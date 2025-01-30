import { Confirm } from "common/components/dialog2/dialog"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api"
import { useNotify } from "common/components/notifications"
import { apiTypes } from "common/services/api-fetch.types"
import useEntity from "carbure/hooks/entity"

export interface DeleteOperationDialogProps {
  onClose: () => void
  onDeleteOperation: () => void
  operation: apiTypes["OperationOutput"]
}

export const DeleteOperationDialog = ({
  onClose,
  onDeleteOperation,
  operation,
}: DeleteOperationDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const { execute: deleteOperation } = useMutation(api.deleteOperation, {
    invalidates: ["operations"],
    onSuccess: () => {
      notify(t(`L'opération n°${operation?.id} a été annulée.`), {
        variant: "success",
      })
      onDeleteOperation()
    },
    onError: () => {
      notify(t(`L'opération n°${operation?.id} n'a pas pu être annulée.`), {
        variant: "danger",
      })
    },
  })

  return (
    <Confirm
      title={t(`Annulation de l'opération n°${operation?.id}`)}
      description={t("Voulez-vous vraiment annuler cette opération ?")}
      confirm={t("Annuler le certificat de cession")}
      onConfirm={() => deleteOperation(entity.id, operation.id)}
      onClose={onClose}
      icon="fr-icon-close-line"
      customVariant="danger"
      hideCancel
    />
  )
}
