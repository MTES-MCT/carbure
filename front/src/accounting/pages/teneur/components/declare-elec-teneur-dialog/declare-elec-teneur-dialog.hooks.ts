import { createOperation } from "accounting/api/elec-operations"
import useEntity from "common/hooks/entity"
import { CreateElecOperationType } from "accounting/types"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { ElecTeneurForm } from "./declare-elec-teneur-dialog.types"
import { Unit } from "common/types"

type CessionDialogProps = {
  values: ElecTeneurForm
  onClose: () => void
}

export const useElecTeneurDialog = ({
  values,
  onClose,
}: CessionDialogProps) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  const operation = () =>
    createOperation(entity.id, {
      type: CreateElecOperationType.TENEUR,
      debited_entity: entity.id,
      quantity: values.quantity,
    })

  return useMutation(operation, {
    invalidates: ["teneur-objectives"],
    onSuccess: () => {
      onClose()
      notify(
        t(
          "La déclaration d'une teneur d'une quantité de {{quantity}} a été réalisée avec succès",
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
      notify(t("Une erreur est survenue lors de la déclaration de teneur"), {
        variant: "danger",
      })
    },
  })
}
