import * as norm from "common/utils/normalizers"
import { Normalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { AgreementFilter, AgreementFilterSelection } from "./types"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"

export interface FiltersProps {
  filters: AgreementFilter[]
  selected: AgreementFilterSelection
  onSelect: (filters: AgreementFilterSelection) => void
  getFilterOptions: (filter: AgreementFilter) => Promise<any[]>
}

export function AgreementFilters({
  filters,
  selected,
  onSelect,
  getFilterOptions,
}: FiltersProps) {
  const { t } = useTranslation()

  const filterLabels = {
    [AgreementFilter.Certificate_id]: t("N° d'agrément"),
    [AgreementFilter.Producers]: t("Producteurs"),
    [AgreementFilter.ProductionSites]: t("Sites de production"),
  }

  const computedFilters = filters.reduce(
    (acc, filter) => {
      acc[filter] = filterLabels[filter]
      return acc
    },
    {} as Record<AgreementFilter, string>
  )

  return (
    <FilterMultiSelect2
      filterLabels={computedFilters}
      selected={selected}
      onSelect={onSelect}
      getFilterOptions={getFilterOptions}
      normalizers={filterNormalizers}
    />
  )
}

type FilterNormalizers = Partial<Record<AgreementFilter, Normalizer<any>>> // prettier-ignore
const filterNormalizers: FilterNormalizers = {
  [AgreementFilter.Certificate_id]: norm.normalizeUnknownFilter,
  [AgreementFilter.Producers]: norm.normalizeUnknownFilter,
  [AgreementFilter.ProductionSites]: norm.normalizeUnknownFilter,
}

export default AgreementFilters
