import { QuantityFormProps } from "accounting/components/quantity-form"
import { FromDepotRecipientToDepotFormProps } from "./from-depot-recipient-to-depot-form/from-depot-recipient-to-depot-form"
import { TransfertGHGRangeFormProps } from "accounting/pages/balances/biofuels/debit-operation-dialog/transfert-dialog/ghg-range-form/ghg-range-form.types"

// Compose the form with all the steps
export type SessionDialogForm = FromDepotRecipientToDepotFormProps &
  QuantityFormProps &
  TransfertGHGRangeFormProps
