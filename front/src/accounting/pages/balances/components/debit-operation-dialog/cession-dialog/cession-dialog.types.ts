import { FromDepotFormProps } from "accounting/components/from-depot-form"
import { QuantityFormProps } from "accounting/components/quantity-form"
import { RecipientToDepotFormProps } from "accounting/components/recipient-to-depot-form"

export enum CessionStepKey {
  FromDepot = "from_depot",
  Quantity = "quantity",
  ToDepot = "to_depot",
  Recap = "recap",
}

// Compose the form with all the steps
export type SessionDialogForm = FromDepotFormProps &
  QuantityFormProps &
  RecipientToDepotFormProps
