import { getBalanceFilters } from "accounting/api/biofuels/balances"
import { Balance, BalancesFilter, BalancesQueryBuilder } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { QueryFilters, useQueryBuilder } from "common/hooks/query-builder-2"
import { Normalizer } from "common/utils/normalize"
import {
  normalizeCountryFilter,
  normalizeFeedstockFilter,
  normalizePeriodFilter,
} from "common/utils/normalizers"
import {
  ADVANCED_FILTER_FIELDS,
  AdvancedFiltersFormProps,
  Filters,
} from "./advanced-filters.types"
import { useMemo } from "react"

export const useAdvancedFiltersBalance = ({
  balance,
}: {
  balance: Balance
}) => {
  const filterNormalizers: Partial<Record<BalancesFilter, Normalizer<string>>> =
    {
      [BalancesFilter.feedstock]: normalizeFeedstockFilter,
      [BalancesFilter.durability_period]: normalizePeriodFilter,
      [BalancesFilter.origin_country]: normalizeCountryFilter,
    }

  const filterLabels: Partial<Record<BalancesFilter, string>> = {
    [BalancesFilter.feedstock]: "Matières premières",
    [BalancesFilter.durability_period]: "Période de durabilité",
    [BalancesFilter.origin_country]: "Pays d'origine",
  }

  const { value } = useFormContext<AdvancedFiltersFormProps>()

  // getBalanceFilters is waiting for a BalancesQuery, so we need to build the query from the form values
  const { query } = useQueryBuilder<BalancesQueryBuilder["config"]>()

  const getFilterOptions = async (filter: string) => {
    const { data } = await getBalanceFilters(
      {
        ...query,
        [BalancesFilter.feedstock]: value.feedstock ?? [],
        [BalancesFilter.durability_period]: value.durability_period ?? [],
        [BalancesFilter.origin_country]: value.origin_country ?? [],
        sector: [balance.sector],
        customs_category: [balance.customs_category],
        biofuel: [balance.biofuel?.code],
        // ges_bound_min: value.gesBoundMin,
        // ges_bound_max: value.gesBoundMax,
      },
      filter as BalancesFilter
    )

    if (!data) {
      return []
    }

    return data
  }

  return {
    getFilterOptions,
    filterNormalizers,
    filterLabels,
  }
}

export const useBuildFilters = ({
  onFiltersChange,
}: {
  onFiltersChange?: (
    filters: AdvancedFiltersFormProps,
    previousFilters: Filters
  ) => void
}) => {
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()

  const selected = useMemo(
    () =>
      Object.fromEntries(
        ADVANCED_FILTER_FIELDS.map((filterField) => [
          filterField,
          value[filterField] ?? [],
        ])
      ) as Filters,
    [value]
  )

  const onSelect = (filters: QueryFilters) => {
    const previousFilters = { ...selected }
    Object.entries(filters).forEach(([filter, value]) => {
      setField(filter as keyof AdvancedFiltersFormProps, value ?? [])
    })
    onFiltersChange?.(
      filters as unknown as AdvancedFiltersFormProps,
      previousFilters
    )
  }

  return { selected, onSelect }
}

/**
 * Function to check if a filter has been removed
 */
export const isFilterRemoved = (
  previousFilters: Filters,
  newFilters: Filters
) => {
  const previousFiltersValues = Object.values(previousFilters).flat()
  const newFiltersValues = Object.values(newFilters).flat()
  return previousFiltersValues.length > newFiltersValues.length
}
