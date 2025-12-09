import { MultiSelect } from "common/components/selects2/multiselect"
import styles from "./filter-multiselect2.module.css"
import { Normalizer } from "common/utils/normalize"
import { QueryFilters } from "common/hooks/query-builder-2"
import { useTranslation } from "react-i18next"
import { useCallback } from "react"
import { Button } from "common/components/button2"

const getEmptyFilters = <Key extends string>(filters: Key[]) => {
  return filters.reduce(
    (acc, filter) => {
      return {
        ...acc,
        [filter]: [],
      }
    },
    {} as Record<Key, string[]>
  )
}

const _hasFiltersValues = (filters: QueryFilters) => {
  return Object.values(filters ?? {}).some((filter) => filter.length > 0)
}
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
  const emptyFilters = getEmptyFilters(filters)
  const hasFiltersValues = useCallback(
    () => _hasFiltersValues(selected),
    [selected]
  )

  const { t } = useTranslation()

  return (
    <div className={styles["filter-multiselect"]}>
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
      {hasFiltersValues() && (
        <Button
          onClick={() => onSelect(emptyFilters)}
          disabled={!hasFiltersValues()}
          priority="secondary"
          className={styles["filter-multiselect__reset"]}
          iconId="ri-close-line"
        >
          {t("Tout réinitialiser")}
        </Button>
      )}
    </div>
  )
}
