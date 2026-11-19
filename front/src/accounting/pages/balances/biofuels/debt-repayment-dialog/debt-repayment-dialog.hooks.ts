import { useCreateOperation } from "accounting/hooks/useCreateOperation.hooks"
import { Balance, CreateOperationType, DebtType } from "accounting/types"
import { simulateDebtRepayment } from "accounting/api/biofuels/debts"
import { mapAdvancedFiltersForPayload } from "accounting/components/advanced-filters/advanced-filters.utils"
import { FormManager } from "common/components/form2"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useRef } from "react"
import { useTranslation } from "react-i18next"
import { DebtRepaymentDialogForm } from "./debt-repayment-dialog.types"

type UseDebtRepaymentDialogProps = {
  balance: Balance
  values: DebtRepaymentDialogForm
  onClose: () => void
  debtType: DebtType
}

export const useDebtRepaymentDialog = ({
  balance,
  values,
  onClose,
  debtType,
}: UseDebtRepaymentDialogProps) => {
  const entity = useEntity()

  return useCreateOperation({
    data: {
      type: CreateOperationType.DEBT_REPAYMENT,
      debited_entity: entity.id,
      biofuel: balance.biofuel.id,
      customs_category: balance.customs_category,
      lots: values.selected_lots ?? [],
      debt_type: debtType,
    },
    quantity: values.quantity!,
    onClose,
    invalidates: ["balances", "operations", "debts"],
  })
}

export const useDebtRepaymentSimulation = (
  balance: Balance,
  form: FormManager<DebtRepaymentDialogForm>
) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()
  const latestValues = useRef(form.value)
  latestValues.current = form.value

  return useMutation(
    async () => {
      const filters = mapAdvancedFiltersForPayload(form.value)
      const { data } = await simulateDebtRepayment(entity.id, {
        biofuel: balance.biofuel.id,
        customs_category: balance.customs_category,
        debited_entity: entity.id,
        ...filters,
      })
      if (!data) {
        throw new Error("Missing debt repayment simulation")
      }
      if (
        JSON.stringify(filters) !==
        JSON.stringify(mapAdvancedFiltersForPayload(latestValues.current))
      ) {
        throw new Error("Debt repayment filters changed during simulation")
      }
      form.setValue((values) => ({
        ...values,
        simulation: data,
        selected_lots: data.selected_lots,
        quantity: data.total_volume,
      }))
    },
    {
      onError: () => {
        notify(
          t(
            "Impossible de calculer le remboursement. Vérifiez les lots disponibles et réessayez."
          ),
          { variant: "danger" }
        )
      },
    }
  )
}
