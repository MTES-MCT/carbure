import useEntity from "common/hooks/entity"
import { TransfertDialogForm } from "./transfert-dialog.types"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { createOperation } from "accounting/api/operations"
import { Balance, CreateOperationType } from "accounting/types"
import { useMutation } from "common/hooks/async"
import { useUnit } from "common/hooks/unit"

type TransfertDialogProps = {
  balance: Balance
  values: TransfertDialogForm
  onClose: () => void
  onOperationCreated: () => void
}

export const useTransfertDialog = ({
  balance,
  values,
  onClose,
  onOperationCreated,
}: TransfertDialogProps) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  const onSubmit = () =>
    createOperation(entity.id, {
      type: CreateOperationType.TRANSFERT,
      credited_entity: values.credited_entity?.id,
      customs_category: balance.customs_category,
      biofuel: balance.biofuel?.id ?? null,
      debited_entity: entity.id,
      lots: values.selected_lots!,
    })

  const mutation = useMutation(onSubmit, {
    invalidates: ["balances"],
    onSuccess: () => {
      onOperationCreated()
      notify(
        t(
          "Le transfert de droits d'une quantité de {{quantity}} a été réalisé avec succès",
          {
            quantity: formatUnit(values.quantity!, {
              fractionDigits: 0,
            }),
          }
        ),
        { variant: "success" }
      )
      onClose()
    },
    onError: () => {
      notify(t("Une erreur est survenue lors du transfert de droits."), {
        variant: "danger",
      })
    },
  })

  return mutation
}
