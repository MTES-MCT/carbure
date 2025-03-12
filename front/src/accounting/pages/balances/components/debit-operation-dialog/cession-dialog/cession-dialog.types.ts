import { FromDepotFormProps } from "accounting/components/from-depot-form"
import { QuantityFormProps } from "accounting/components/quantity-form"
import { RecipientToDepotFormProps } from "accounting/components/recipient-to-depot-form"

// Compose the form with all the steps
export type SessionDialogForm = FromDepotFormProps &
  QuantityFormProps &
  RecipientToDepotFormProps
