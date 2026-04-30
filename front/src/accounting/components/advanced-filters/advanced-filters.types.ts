import { BalancesFilter } from "accounting/types"
import { GHGRangeFormProps } from "../ghg-range-form"

export const ADVANCED_FILTER_FIELDS = [
  BalancesFilter.feedstock,
  BalancesFilter.durability_period,
  BalancesFilter.origin_country,
] as const satisfies readonly BalancesFilter[]

type AdvancedFilterField = (typeof ADVANCED_FILTER_FIELDS)[number]

export type Filters = Record<AdvancedFilterField, string[]>

export type AdvancedFiltersFormProps = Filters & GHGRangeFormProps
