import { QuantityFormProps } from "accounting/components/quantity-form"
import { FromDepotRecipientToDepotFormProps } from "./from-depot-recipient-to-depot-form/from-depot-recipient-to-depot-form"

// Compose the form with all the steps
export type SessionDialogForm = FromDepotRecipientToDepotFormProps &
  QuantityFormProps
