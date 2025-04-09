import { createOperationWithSimulation } from "accounting/api/operations"
import { useMutation } from "common/hooks/async"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { CreateOperationType } from "accounting/types"
import { CONVERSIONS, formatUnit } from "common/utils/formatters"
import { ExtendedUnit, Unit } from "common/types"

type DeclareTeneurDialogProps = {
  values: DeclareTeneurDialogForm
  onClose: () => void
  onOperationCreated: () => void
}

export const useDeclareTeneurDialog = ({
  onClose,
  onOperationCreated,
  values,
}: DeclareTeneurDialogProps) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()

  const onSubmit = () =>
    createOperationWithSimulation(entity.id, {
      simulation: {
        target_volume: CONVERSIONS.energy.GJ_TO_MJ(values.quantity!),
        target_emission: values.avoided_emissions!,
        unit: Unit.MJ,
      },
      operation: {
        type: CreateOperationType.TENEUR,
      },
      customs_category: values.balance!.customs_category,
      biofuel: values.balance!.biofuel?.id ?? null,
      debited_entity: entity.id,
    })

  const mutation = useMutation(onSubmit, {
    invalidates: ["teneur-objectives"],
    onSuccess: () => {
      onClose()
      onOperationCreated()
      notify(
        t(
          "La mise en teneur d'une quantité de {{quantity}} a été réalisée avec succès",
          {
            quantity: formatUnit(values.quantity!, ExtendedUnit.GJ, {
              fractionDigits: 0,
            }),
          }
        ),
        { variant: "success" }
      )
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de la mise en teneur."), {
        variant: "danger",
      })
    },
  })

  return mutation
}
