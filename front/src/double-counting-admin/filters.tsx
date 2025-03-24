import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import * as norm from "common/utils/normalizers"
import { Grid } from "common/components/scaffold"
import { Normalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { AgreementFilter, AgreementFilterSelection } from "./types"

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

  return (
    <Grid>
      {filters.map((filter) => (
        <FilterSelect
          key={filter}
          field={filter}
          placeholder={filterLabels[filter]}
          value={selected[filter]}
          onChange={(value) => onSelect({ ...selected, [filter]: value ?? [] })}
          getOptions={() => getFilterOptions(filter)}
        />
      ))}
    </Grid>
  )
}

export type FilterSelectProps = { field: AgreementFilter } & Omit<
  MultiSelectProps<string>,
  "options"
>

export const FilterSelect = ({
  field,
  value = [],
  onChange,
  ...props
}: FilterSelectProps) => (
  <MultiSelect
    {...props}
    clear
    search
    variant="solid"
    value={value}
    onChange={onChange}
    normalize={filterNormalizers[field]}
    sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
  />
)

type FilterNormalizers = Partial<Record<AgreementFilter, Normalizer<any>>> // prettier-ignore
const filterNormalizers: FilterNormalizers = {
  [AgreementFilter.Certificate_id]: norm.normalizeUnknownFilter,
  [AgreementFilter.Producers]: norm.normalizeUnknownFilter,
  [AgreementFilter.ProductionSites]: norm.normalizeUnknownFilter,
}

export default AgreementFilters
