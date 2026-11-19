import { QuantityFormProps } from "accounting/components/quantity-form"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { Balance, Debt, DebtType } from "accounting/types"
import { FormManager } from "common/components/form2"
import { apiTypes } from "common/services/api-fetch.types"

export type DebtRepaymentDialogForm = AdvancedFiltersFormProps &
  QuantityFormProps & {
    simulation?: apiTypes["DebtRepaymentSimulation"]
  }

export interface DebtRepaymentDialogProps {
  onClose: () => void
  balance: Balance
  debt: Debt
}

export interface DebtRepaymentDialogContentProps extends DebtRepaymentDialogProps {
  form: FormManager<DebtRepaymentDialogForm>
  debtType: DebtType
}
