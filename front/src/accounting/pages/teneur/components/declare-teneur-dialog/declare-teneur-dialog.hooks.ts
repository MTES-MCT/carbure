import { createOperation } from "accounting/api/biofuels/operations"
import { useMutation } from "common/hooks/async"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { CreateOperationType } from "accounting/types"
import { floorNumber } from "common/utils/formatters"
import {
  BiofuelUnconstrainedCategoryObjective,
  CategoryObjective,
  MainObjective,
  TargetType,
} from "../../types"
import { useMemo } from "react"
import { maxLitersFromRemainingMj } from "../../utils/liters"
import {
  formatAccountingUnit,
  formatTCO2Number,
} from "accounting/utils/formatters"
import { FRACTION_DIGITS_LITERS } from "accounting/config"
import { Unit } from "common/types"

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
            quantity: formatAccountingUnit(values.quantity!, Unit.l),
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
    return formatTCO2Number(remainingCO2)
  }, [mainObjective, values.avoided_emissions])
}

/**
 * Max declarable quantity for the teneur form, in liters.
 * Balance is in L; category caps are in GJ — convert remaining cap to liters
 * (ceil to 2 decimals via pci_litre) before comparing with the available balance.
 */
export const useCalculateQuantityMax = (
  objective: CategoryObjective | BiofuelUnconstrainedCategoryObjective,
  values: DeclareTeneurDialogForm
) => {
  const availableBalance = values.balance?.available_balance
  const pciLitre = values.balance?.biofuel?.pci_litre

  return useMemo(() => {
    if (availableBalance === undefined) {
      return 0
    }

    // No cap on quantity when there is no target or the category is objectivized (REACH)
    if (!objective.target_mj || objective.target_type === TargetType.REACH) {
      return floorNumber(availableBalance, FRACTION_DIGITS_LITERS)
    }

    if (!pciLitre) {
      return floorNumber(availableBalance, FRACTION_DIGITS_LITERS)
    }

    const remainingObjectiveEnergyMj = objective.remaining_energy_mj
    const maxLitersFromObjective = maxLitersFromRemainingMj(
      remainingObjectiveEnergyMj,
      pciLitre
    )

    return Math.min(availableBalance, maxLitersFromObjective)
  }, [objective, availableBalance, pciLitre])
}
