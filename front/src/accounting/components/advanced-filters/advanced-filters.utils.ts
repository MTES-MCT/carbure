import { AdvancedFiltersFormProps } from "./advanced-filters.types"

export const showNextStepAdvancedFilters = (
  values: AdvancedFiltersFormProps
) => {
  return Boolean(values.availableBalance && values.availableBalance > 0)
}
