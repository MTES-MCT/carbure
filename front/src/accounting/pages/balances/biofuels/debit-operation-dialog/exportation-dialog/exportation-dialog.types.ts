import { FromDepotFormProps } from "accounting/components/from-depot-form"
import { QuantityFormProps } from "accounting/components/quantity-form"
import { CountryFormProps } from "./country-form"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"

export type ExportationDialogForm = FromDepotFormProps &
  AdvancedFiltersFormProps &
  QuantityFormProps &
  CountryFormProps
