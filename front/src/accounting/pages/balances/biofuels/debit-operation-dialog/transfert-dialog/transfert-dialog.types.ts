import { QuantityFormProps } from "accounting/components/quantity-form"
import { RecipientFormProps } from "accounting/components/recipient-form"
import { GHGRangeFormProps } from "accounting/components/ghg-range-form"

export type TransfertDialogForm = RecipientFormProps &
  QuantityFormProps &
  GHGRangeFormProps
