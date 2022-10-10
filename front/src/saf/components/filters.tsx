import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"
import { SafFilter, SafFilterSelection } from "../types"
import { Normalizer } from "common/utils/normalize"
import { Grid, Row } from "common/components/scaffold"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select" // prettier-ignore
import Button from "common/components/button"
import * as norm from "carbure/utils/normalizers"

export interface FiltersProps<Q> {
  query: Q
  filters: SafFilter[]
  selected: SafFilterSelection
  onSelect: (filters: SafFilterSelection) => void
  getFilters: (field: SafFilter, query: Q) => Promise<any[]>
}

export function Filters<T>({
  query,
  filters,
  selected,
  onSelect,
  getFilters,
}: FiltersProps<T>) {
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
          getOptions={() => getFilters(filter, query)}
        />
      ))}
    </Grid>
  )
}

export interface FilterManager {
  filters: SafFilterSelection
  onFilter: (filters: SafFilterSelection) => void
}

export const ResetButton = ({ filters, onFilter }: FilterManager) => {
  const { t } = useTranslation()
  return (
    <Row asideX>
      <Button
        variant="link"
        action={() => onFilter({})}
        label={t("Réinitialiser les filtres")}
      />
      <span> ({countFilters(filters)})</span>
    </Row>
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

export function useFilterParams() {
  const [filtersParams, setFiltersParams] = useSearchParams()
  const filters = useMemo(() => searchToFilters(filtersParams), [filtersParams])
  return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}

export function searchToFilters(search: URLSearchParams) {
  const filters: SafFilterSelection = {}
  search.forEach((value, filter) => {
    const fkey = filter as SafFilter
    filters[fkey] = filters[fkey] ?? []
    filters[fkey]!.push(value)
  })
  return filters
}

export function countFilters(filters: SafFilterSelection | undefined) {
  if (filters === undefined) return 0
  return Object.values(filters).reduce((total, list) => total + list.length, 0)
}

export default Filters
