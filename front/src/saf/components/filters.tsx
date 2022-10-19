import * as norm from "carbure/utils/normalizers"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold"
import { Normalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { SafFilter, SafFilterSelection } from "../types"

export interface FiltersProps {
  filters: SafFilter[]
  selected: SafFilterSelection
  onSelect: (filters: SafFilterSelection) => void
  getFilterOptions: (filter: SafFilter) => Promise<any[]>
}

export function Filters({
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
    [SafFilter.Supplier]: t("Fournisseur"),
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

export type FilterSelectProps = { field: SafFilter } & Omit<
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

type FilterNormalizers= Partial<Record<SafFilter, Normalizer<any>>> // prettier-ignore
const filterNormalizers: FilterNormalizers = {
  [SafFilter.Feedstocks]: norm.normalizeFeedstockFilter,
  [SafFilter.Periods]: norm.normalizePeriodFilter,
  [SafFilter.Clients]: norm.normalizeUnknownFilter,
}

export default Filters
