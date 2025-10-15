import { MultiSelect } from "common/components/selects2/multiselect"
import styles from "./filter-multiselect2.module.css"
import { ShowMore } from "common/components/show-more/show-more"
import { Normalizer } from "common/utils/normalize"
import { QueryFilters } from "common/hooks/query-builder-2"

export interface FilterMultiSelectProps2<
  Key extends string,
  Value extends string = Key,
> {
  filterLabels: Partial<Record<Key, string>>
  selected: QueryFilters
  onSelect: (filters: QueryFilters) => void
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
    <ShowMore>
      {filters.map((filter) => (
        <MultiSelect
          key={filter}
          search
          value={selected[filter]}
          placeholder={filterLabels[filter]}
          sort={(item) => (item.value === "UNKNOWN" ? "" : item.value)}
          onChange={(value) => onSelect({ ...selected, [filter]: value ?? [] })}
          getOptions={() => getFilterOptions(filter)}
          className={styles["filter-multiselect__filter"]}
          normalize={normalizers?.[filter]}
          clear
        />
      ))}
    </ShowMore>
  )
}
