import { FromDepotFormProps } from "accounting/components/from-depot-form"
import { QuantityFormProps } from "accounting/components/quantity-form"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { DevaluationTypeFormProps } from "./devaluation-type-form"

export type DevaluationDialogForm = FromDepotFormProps &
  AdvancedFiltersFormProps &
  QuantityFormProps &
  DevaluationTypeFormProps
