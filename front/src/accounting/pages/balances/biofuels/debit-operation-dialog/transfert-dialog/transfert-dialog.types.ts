import { QuantityFormProps } from "accounting/components/quantity-form"
import { RecipientToDepotFormProps } from "accounting/components/recipient-to-depot-form"
import { TransfertGHGRangeFormProps } from "./ghg-range-form"
export type TransfertDialogForm = RecipientToDepotFormProps &
  QuantityFormProps &
  TransfertGHGRangeFormProps
