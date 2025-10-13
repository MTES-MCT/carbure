import { createOperation } from "accounting/api/biofuels/operations"
import { useMutation } from "common/hooks/async"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { CreateOperationType } from "accounting/types"
import { formatNumber, formatUnit } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import {
  CategoryObjective,
  MainObjective,
  UnconstrainedCategoryObjective,
} from "../../types"
import { useMemo } from "react"
import { computeObjectiveEnergy } from "../../utils/formatters"

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
    createOperation(entity.id, {
      type: CreateOperationType.TENEUR,
      customs_category: values.balance!.customs_category,
      biofuel: values.balance!.biofuel?.id ?? null,
      debited_entity: entity.id,
      lots: values.selected_lots!,
    })

  const mutation = useMutation(onSubmit, {
    invalidates: ["teneur-objectives"],
    onSuccess: () => {
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
      onClose()
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de la mise en teneur."), {
        variant: "danger",
      })
    },
  })

  return mutation
}

// Compute the remaining CO2 objective after the avoided emissions have been declared
export const useRemainingCO2Objective = (
  values: DeclareTeneurDialogForm,
  mainObjective?: MainObjective
) => {
  return useMemo(() => {
    if (!mainObjective) return null

    const avoidedEmissions = values.avoided_emissions ?? 0
    const remainingCO2 = Math.max(
      0,
      mainObjective.target -
        mainObjective.teneur_declared -
        mainObjective.teneur_declared_month -
        avoidedEmissions
    )
    return formatNumber(remainingCO2, {
      fractionDigits: 0,
      mode: "ceil",
    })
  }, [mainObjective, values.avoided_emissions])
}

// Compute the remaining energy before the limit or the objective after the quantity has been declared
export const useRemainingEnergyBeforeLimitOrObjective = (
  objective: CategoryObjective | UnconstrainedCategoryObjective,
  values: DeclareTeneurDialogForm
) => {
  return useMemo(() => {
    // Add quantity declared only if the "declare quantity" button has been clicked
    const quantity = values.quantity ?? 0

    const remainingEnergy = Math.max(
      0,
      objective.target ? computeObjectiveEnergy(objective) - quantity : 0
    )

    return formatUnit(remainingEnergy, ExtendedUnit.GJ, {
      fractionDigits: 0,
    })
  }, [values.quantity, objective])
}
