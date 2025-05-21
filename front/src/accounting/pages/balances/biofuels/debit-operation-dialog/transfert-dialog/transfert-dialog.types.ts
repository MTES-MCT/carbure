import { QuantityFormProps } from "accounting/components/quantity-form"
import { RecipientFormProps } from "accounting/components/recipient-form"
import { TransfertGHGRangeFormProps } from "./ghg-range-form"

export type TransfertDialogForm = RecipientFormProps &
  QuantityFormProps &
  TransfertGHGRangeFormProps
