import { MultiSelect } from "common/components/selects2/multiselect"
import { CBFilterSelection } from "common/hooks/query-builder-2"
import styles from "./filter-multiselect2.module.css"
import { Normalizer } from "common/utils/normalize"

export interface FilterMultiSelectProps2<
  Key extends string,
  Value extends string = Key,
> {
  filterLabels: Record<Key, string>
  selected: CBFilterSelection
  onSelect: (filters: CBFilterSelection) => void
  getFilterOptions: (filter: Key) => Promise<any[]>
  normalizers?: Record<string, Normalizer<Key, Value>>
}

export const FilterMultiSelect2 = <
  Key extends string,
  Value extends string = Key,
>({
  filterLabels,
  selected = {},
  onSelect,
  getFilterOptions,
  normalizers,
}: FilterMultiSelectProps2<Key, Value>) => {
  const filters = Object.keys(filterLabels) as Key[]

  return (
    <div className={styles["filter-multiselect"]}>
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
          normalize={normalizers?.[filter]}
        />
      ))}
    </div>
  )
}
