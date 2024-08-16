import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold";
import { CBFilterSelection } from "common/hooks/query-builder";
import { defaultNormalizer } from "common/utils/normalize";

export interface FiltersProps {
  filterLabels: Record<string, string>
  selected: CBFilterSelection
  onSelect: (filters: CBFilterSelection) => void
  getFilterOptions: (filter: string) => Promise<any[]>
}

export function FilterSelect({
  filterLabels,
  selected,
  onSelect,
  getFilterOptions,
}: FiltersProps) {

  const filters = Object.keys(filterLabels)

  return (
    <Grid>
      {filters.map((filter) => {
        return (
          <FilterMultiSelect
            key={filter}
            field={filter}
            placeholder={filterLabels[filter]}
            value={selected[filter]}
            onChange={(value) =>
              onSelect({ ...selected, [filter]: value ?? [] })
            }
            getOptions={() => getFilterOptions(filter)}
          />
        )
      })}
    </Grid>
  )
}

export type FilterMultiSelectProps = { field: string } & Omit<
  MultiSelectProps<string>,
  "options"
>

export default FilterSelect

const FilterMultiSelect = ({
  field,
  value = [],
  onChange,
  ...props
}: FilterMultiSelectProps) => (
  <MultiSelect
    {...props}
    clear
    search
    variant="solid"
    value={value}
    onChange={onChange}
    normalize={defaultNormalizer}
    sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
  />
)
