import { createOperationWithSimulation } from "accounting/api/operations"
import useEntity from "common/hooks/entity"
import { SessionDialogForm } from "./cession-dialog.types"
import { Balance, CreateOperationType } from "accounting/types"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"

type CessionDialogProps = {
  balance: Balance
  values: SessionDialogForm
  onClose: () => void
  onOperationCreated: () => void
}
export const useCessionDialog = ({
  balance,
  values,
  onClose,
  onOperationCreated,
}: CessionDialogProps) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  const onSubmit = () =>
    createOperationWithSimulation(entity.id, {
      simulation: {
        target_volume: values.quantity!,
        target_emission: values.avoided_emissions!,
        unit: balance.unit,
      },
      operation: {
        type: CreateOperationType.CESSION,
        from_depot: values.from_depot?.id,
        to_depot: values.to_depot?.id,
        credited_entity: values.credited_entity?.id,
      },
      customs_category: balance.customs_category,
      biofuel: balance.biofuel?.id ?? null,
      debited_entity: entity.id,
    })

  return useMutation(onSubmit, {
    invalidates: ["balances"],
    onSuccess: () => {
      onClose()
      onOperationCreated()
      notify(
        t(
          "La cession d'une quantité de {{quantity}} a été réalisée avec succès",
          {
            quantity: formatUnit(values.quantity!, {
              fractionDigits: 0,
            }),
          }
        ),
        { variant: "success" }
      )
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de la cession"), {
        variant: "danger",
      })
    },
  })
}
