import { useCreateOperation } from "accounting/hooks/useCreateOperation.hooks"
import { Balance, CreateOperationType } from "accounting/types"
import useEntity from "common/hooks/entity"
import { DebtRepaymentDialogForm } from "./debt-repayment-dialog.types"

type UseDebtRepaymentDialogProps = {
  balance: Balance
  values: DebtRepaymentDialogForm
  onClose: () => void
}

export const useDebtRepaymentDialog = ({
  balance,
  values,
  onClose,
}: UseDebtRepaymentDialogProps) => {
  const entity = useEntity()

  return useCreateOperation({
    data: {
      type: CreateOperationType.DEBT_REPAYMENT,
      debited_entity: entity.id,
      biofuel: balance.biofuel.id,
      customs_category: balance.customs_category,
      lots: values.selected_lots ?? [],
    },
    quantity: values.quantity!,
    onClose,
    invalidates: ["balances", "operations", "debts"],
  })
}
