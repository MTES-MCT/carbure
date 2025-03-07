import { MultiSelect } from "common/components/selects2/multiselect"
import { CBFilterSelection } from "common/hooks/query-builder-2"
import styles from "./filter-multiselect2.module.css"
import { ShowMore } from "common/components/show-more/show-more"

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
          className={styles["filter-multiselect__filter"]}
        />
      ))}
    </ShowMore>
  )
}
