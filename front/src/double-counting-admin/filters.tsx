import * as norm from "common/utils/normalizers"
import { Normalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { AgreementFilter, AgreementFilterSelection } from "./types"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { getStatusLabel } from "double-counting/components/application-status"
import { DoubleCountingExtendedStatus as DCStatusExt } from "double-counting/types"
import i18next from "i18next"

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
    [AgreementFilter.Status]: t("Statuts"),
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

const normalizeStatusFilter: Normalizer<string> = (status) => ({
  value: status,
  label: getStatusLabel(status as DCStatusExt, i18next.t.bind(i18next)),
})

type FilterNormalizers = Partial<Record<AgreementFilter, Normalizer<any>>> // prettier-ignore
const filterNormalizers: FilterNormalizers = {
  [AgreementFilter.Certificate_id]: norm.normalizeUnknownFilter,
  [AgreementFilter.Producers]: norm.normalizeUnknownFilter,
  [AgreementFilter.ProductionSites]: norm.normalizeUnknownFilter,
  [AgreementFilter.Status]: normalizeStatusFilter,
}

export default AgreementFilters
