import { createOperation } from "accounting/api/biofuels/operations"
import { useMutation } from "common/hooks/async"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { CreateOperationType } from "accounting/types"
import { floorNumber, formatNumber } from "common/utils/formatters"
import {
  BiofuelUnconstrainedCategoryObjective,
  CategoryObjective,
  MainObjective,
  TargetType,
} from "../../types"
import { useMemo } from "react"
import {
  computeObjectiveEnergy,
  formatObjectiveGJ,
} from "../../utils/formatters"

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
            quantity: formatObjectiveGJ(values.quantity!),
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
        mainObjective.pending_teneur -
        avoidedEmissions
    )
    return formatNumber(remainingCO2, {
      fractionDigits: 0,
      mode: "ceil",
    })
  }, [mainObjective, values.avoided_emissions])
}

export const useCalculateQuantityMax = (
  objective: CategoryObjective | BiofuelUnconstrainedCategoryObjective,
  values: DeclareTeneurDialogForm
) => {
  const availableBalance = values.balance?.available_balance

  return useMemo(() => {
    if (availableBalance === undefined) {
      return 0
    }

    // if the objective is a cap or there is no target, the maximum quantity is the available balance
    if (!objective.target || objective.target_type === TargetType.REACH) {
      return floorNumber(availableBalance, 0)
    }

    const remainingObjectiveEnergy = computeObjectiveEnergy(objective)

    return floorNumber(Math.min(availableBalance, remainingObjectiveEnergy), 0)
  }, [objective, availableBalance])
}
