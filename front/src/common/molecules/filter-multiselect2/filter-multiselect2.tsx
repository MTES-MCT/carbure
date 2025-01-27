import { MultiSelect } from "common/components/selects2/multiselect"
import { ShowMore } from "common/components/show-more/show-more"
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
  console.log(filters)
  return (
    <ShowMore>
      {filters.map((filter) => (
        <MultiSelect
          key={filter}
          search
          value={selected[filter]}
          placeholder={filterLabels[filter]}
          sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
          onChange={(value) => onSelect({ ...selected, [filter]: value ?? [] })}
          getOptions={() => getFilterOptions(filter)}
        />
      ))}
    </ShowMore>
  )
}
