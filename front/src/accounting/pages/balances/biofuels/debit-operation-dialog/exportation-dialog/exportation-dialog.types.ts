import { FromDepotFormProps } from "accounting/components/from-depot-form"
import { QuantityFormProps } from "accounting/components/quantity-form"
import { CountryFormProps } from "./country-form"
import { GHGRangeFormProps } from "accounting/components/ghg-range-form"

export type ExportationDialogForm = FromDepotFormProps &
  GHGRangeFormProps &
  QuantityFormProps &
  CountryFormProps
