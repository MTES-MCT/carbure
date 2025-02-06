import { MultiSelect } from "common/components/selects2/multiselect"
import { CBFilterSelection } from "common/hooks/query-builder-2"
import styles from "./filter-multiselect2.module.css"
import { ShowMore } from "common/components/show-more/show-more"

export interface FilterMultiSelectProps2<Key extends string> {
  filterLabels: Record<Key, string>
  selected: CBFilterSelection
  onSelect: (filters: CBFilterSelection) => void
  getFilterOptions: (filter: Key) => Promise<any[]>
}
export const FilterMultiSelect2 = <Key extends string>({
  filterLabels,
  selected = {},
  onSelect,
  getFilterOptions,
}: FilterMultiSelectProps2<Key>) => {
  const filters = Object.keys(filterLabels) as Key[]

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
