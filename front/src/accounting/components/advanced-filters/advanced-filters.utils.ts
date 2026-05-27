import { floorNumber } from "common/utils/formatters"
import {
  AdvancedFiltersFormProps,
  AdvancedFiltersPayload,
} from "./advanced-filters.types"

export const showNextStepAdvancedFilters = (
  values: AdvancedFiltersFormProps
) => {
  const availableBalance = values.availableBalance
    ? floorNumber(values.availableBalance, 0)
    : 0
  return Boolean(availableBalance > 0)
}

export const mapAdvancedFiltersForPayload = (
  values: AdvancedFiltersFormProps
): AdvancedFiltersPayload => {
  return {
    feedstock: values.feedstock,
    origin_country: values.origin_country,
    durability_period: values.durability_period,
    ges_bound_min: values.gesBoundMin,
    ges_bound_max: values.gesBoundMax,
  }
}
