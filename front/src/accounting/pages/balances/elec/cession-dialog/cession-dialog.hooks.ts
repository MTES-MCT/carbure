import { createOperation } from "accounting/api/elec/operations"
import useEntity from "common/hooks/entity"
import { CreateElecOperationType } from "accounting/types"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { ElecCessionForm } from "./cession-dialog.types"
import { Unit } from "common/types"

type CessionDialogProps = {
  values: ElecCessionForm
  onClose: () => void
}
export const useCessionDialog = ({ values, onClose }: CessionDialogProps) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  const onSubmit = () =>
    // @TODO put the right values here
    createOperation(entity.id, {
      type: CreateElecOperationType.CESSION,
      credited_entity: values.credited_entity?.id,
      debited_entity: entity.id,
      quantity: values.quantity,
    })

  return useMutation(onSubmit, {
    invalidates: ["elec-balances"],
    onSuccess: () => {
      onClose()
      notify(
        t(
          "La cession d'une quantité de {{quantity}} a été réalisée avec succès",
          {
            quantity: formatUnit(values.quantity!, {
              fractionDigits: 0,
              unit: Unit.MJ,
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
