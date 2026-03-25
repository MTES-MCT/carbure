import { getBalanceFilters } from "accounting/api/biofuels/balances"
import { BalancesFilter, BalancesQueryBuilder } from "accounting/types"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { Normalizer } from "common/utils/normalize"
import {
  normalizeCountryFilter,
  normalizeFeedstockFilter,
  normalizePeriodFilter,
} from "common/utils/normalizers"

export const useAdvancedFiltersBalance = () => {
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

  const { state, actions, query } =
    useQueryBuilder<BalancesQueryBuilder["config"]>()

  const getFilterOptions = async (filter: string) => {
    const { data } = await getBalanceFilters(query, filter as BalancesFilter)

    if (!data) {
      return []
    }

    return data
  }

  return {
    getFilterOptions,
    filterNormalizers,
    filterLabels,
    state,
    actions,
    query,
  }
}
