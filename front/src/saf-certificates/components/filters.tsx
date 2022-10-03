import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"
import { SafCertificateFilter, FilterSelection } from "../types"
import { Normalizer } from "common/utils/normalize"
import { Grid, Row } from "common/components/scaffold"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select" // prettier-ignore
import Button from "common/components/button"
import * as norm from "carbure/utils/normalizers"

export interface FiltersProps<Q> {
  query: Q
  filters: SafCertificateFilter[]
  selected: FilterSelection
  onSelect: (filters: FilterSelection) => void
  getFilters: (field: SafCertificateFilter, query: Q) => Promise<any[]>
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
    [SafCertificateFilter.Periods]: t("Périodes"),
    [SafCertificateFilter.Feedstocks]: t("Matières Premières"),
    [SafCertificateFilter.Biofuels]: t("Biocarburants"),
    [SafCertificateFilter.CountriesOfOrigin]: t("Pays d'origine"),
    [SafCertificateFilter.Clients]: t("Clients"),
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
  filters: FilterSelection
  onFilter: (filters: FilterSelection) => void
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

export type FilterSelectProps = { field: SafCertificateFilter } & Omit<
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

type FilterNormalizers= Partial<Record<SafCertificateFilter, Normalizer<any>>> // prettier-ignore
const filterNormalizers: FilterNormalizers = {
  [SafCertificateFilter.Feedstocks]: norm.normalizeFeedstockFilter,
  [SafCertificateFilter.Biofuels]: norm.normalizeBiofuelFilter,
  [SafCertificateFilter.CountriesOfOrigin]: norm.normalizeCountryFilter,
  [SafCertificateFilter.Periods]: norm.normalizePeriodFilter,
  [SafCertificateFilter.Clients]: norm.normalizeUnknownFilter,
}

export function useFilterParams() {
  const [filtersParams, setFiltersParams] = useSearchParams()
  const filters = useMemo(() => searchToFilters(filtersParams), [filtersParams])
  return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}

export function searchToFilters(search: URLSearchParams) {
  const filters: FilterSelection = {}
  search.forEach((value, filter) => {
    const fkey = filter as SafCertificateFilter
    filters[fkey] = filters[fkey] ?? []
    filters[fkey]!.push(value)
  })
  return filters
}

export function countFilters(filters: FilterSelection | undefined) {
  if (filters === undefined) return 0
  return Object.values(filters).reduce((total, list) => total + list.length, 0)
}

export default Filters
