import * as norm from "common/utils/normalizers"
import { Normalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { SafFilter, SafFilterSelection } from "../types"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { normalizeConsumptionType } from "saf/utils/normalizers"

export interface FiltersProps {
  filters: SafFilter[]
  selected: SafFilterSelection
  onSelect: (filters: SafFilterSelection) => void
  getFilterOptions: (filter: SafFilter) => Promise<any[]>
}

export function SafFilters({
  filters,
  selected,
  onSelect,
  getFilterOptions,
}: FiltersProps) {
  const { t } = useTranslation()

  const filterLabels = {
    [SafFilter.Periods]: t("Périodes"),
    [SafFilter.Feedstocks]: t("Matières Premières"),
    [SafFilter.Clients]: t("Clients"),
    [SafFilter.CountriesOfOrigin]: t("Pays d'origine"),
    [SafFilter.ProductionSites]: t("Sites de production"),
    [SafFilter.DeliverySites]: t("Sites de livraison"),
    [SafFilter.ConsumptionTypes]: t("Types de consommation"),
  }

  const computedFilters = filters.reduce(
    (acc, filter) => {
      acc[filter] = filterLabels[filter]
      return acc
    },
    {} as Record<SafFilter, string>
  )

  return (
    <FilterMultiSelect2
      filterLabels={computedFilters}
      getFilterOptions={getFilterOptions}
      selected={selected}
      onSelect={onSelect}
      normalizers={filterNormalizers}
    />
  )
}

type FilterNormalizers = Partial<Record<SafFilter, Normalizer<any>>>

const filterNormalizers: FilterNormalizers = {
  [SafFilter.Feedstocks]: norm.normalizeFeedstockFilter,
  [SafFilter.Periods]: norm.normalizePeriodFilter,
  [SafFilter.Clients]: norm.normalizeUnknownFilter,
  [SafFilter.CountriesOfOrigin]: norm.normalizeCountryFilter,
  [SafFilter.ProductionSites]: norm.normalizeUnknownFilter,
  [SafFilter.DeliverySites]: norm.normalizeUnknownFilter,
  [SafFilter.ConsumptionTypes]: normalizeConsumptionType,
}

export default SafFilters
