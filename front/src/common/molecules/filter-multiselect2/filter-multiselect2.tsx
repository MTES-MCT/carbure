import { Grid } from "common/components/scaffold"
import { MultiSelect } from "common/components/selects2/multiselect"
import { CBFilterSelection } from "common/hooks/query-builder-2"

export interface FilterMultiSelectProps2 {
  filterLabels: Record<string, string>
  selected: CBFilterSelection
  onSelect: (filters: CBFilterSelection) => void
  getFilterOptions: (filter: string) => Promise<any[]>
}
export const FilterMultiSelect2 = ({
  filterLabels,
  selected = {},
  onSelect,
  getFilterOptions,
}: FilterMultiSelectProps2) => {
  const filters = Object.keys(filterLabels)
  return (
    <Grid>
      {filters.map((filter) => (
        <MultiSelect
          key={filter}
          search
          value={selected[filter]}
          placeholder={filterLabels[filter]}
          sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
          onChange={(value) => onSelect({ ...selected, [filter]: value ?? [] })}
          getOptions={() => getFilterOptions(filter)}
          full
        />
      ))}
    </Grid>
  )
}
