import { FromDepotFormProps } from "accounting/components/from-depot-form"
import { QuantityFormProps } from "accounting/components/quantity-form"
import { CountryFormProps } from "./country-form"

export type ExportationDialogForm = FromDepotFormProps &
  QuantityFormProps &
  CountryFormProps
