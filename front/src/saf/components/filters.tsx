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
    [SafFilter.period]: t("Périodes"),
    [SafFilter.feedstock]: t("Matières Premières"),
    [SafFilter.client]: t("Clients"),
    [SafFilter.supplier]: t("Fournisseurs"),
    [SafFilter.added_by]: t("Ajouté par"),
    [SafFilter.country_of_origin]: t("Pays d'origine"),
    [SafFilter.production_site]: t("Sites de production"),
    [SafFilter.origin_depot]: t("Dépôt d'origine"),
    [SafFilter.consumption_type]: t("Types de consommation"),
    [SafFilter.reception_airport]: t("Aéroport"),
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
  [SafFilter.feedstock]: norm.normalizeFeedstockFilter,
  [SafFilter.period]: norm.normalizePeriodFilter,
  [SafFilter.client]: norm.normalizeUnknownFilter,
  [SafFilter.added_by]: norm.normalizeUnknownFilter,
  [SafFilter.supplier]: norm.normalizeUnknownFilter,
  [SafFilter.country_of_origin]: norm.normalizeCountryFilter,
  [SafFilter.production_site]: norm.normalizeUnknownFilter,
  [SafFilter.origin_depot]: norm.normalizeUnknownFilter,
  [SafFilter.consumption_type]: normalizeConsumptionType,
  [SafFilter.reception_airport]: norm.normalizeUnknownFilter,
}

export default SafFilters
