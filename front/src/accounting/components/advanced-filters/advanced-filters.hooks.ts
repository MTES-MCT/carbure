import { getBalanceFilters } from "accounting/api/biofuels/balances"
import { Balance, BalancesFilter, BalancesQueryBuilder } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { Normalizer } from "common/utils/normalize"
import {
  normalizeCountryFilter,
  normalizeFeedstockFilter,
  normalizePeriodFilter,
} from "common/utils/normalizers"
import {
  ADVANCED_FILTER_FIELDS,
  AdvancedFiltersFormProps,
} from "./advanced-filters.types"

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
        // [BalancesFilter.durability_period]: value.durability_period ?? [],
        // [BalancesFilter.origin_country]: value.origin_country ?? [],
        sector: [balance.sector],
        customs_category: [balance.customs_category],
        biofuel: [balance.biofuel?.code],
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

export const hasFiltersSelected = (value: AdvancedFiltersFormProps) => {
  return ADVANCED_FILTER_FIELDS.some((filterField) => {
    return (value[filterField] ?? []).length > 0
  })
}
