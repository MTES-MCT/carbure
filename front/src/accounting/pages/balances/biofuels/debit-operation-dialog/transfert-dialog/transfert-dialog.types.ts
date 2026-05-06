import { QuantityFormProps } from "accounting/components/quantity-form"
import { RecipientFormProps } from "accounting/components/recipient-form"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"

export type TransfertDialogForm = RecipientFormProps &
  QuantityFormProps &
  AdvancedFiltersFormProps
